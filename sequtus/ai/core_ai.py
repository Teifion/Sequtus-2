import multiprocessing
import time

from sequtus.libs import vectors, ai_lib

ai_classes = {}
def register_ai(class_name, class_template):
    if class_name not in ai_classes:
        ai_classes[class_name] = class_template
    else:
        raise KeyError("AI class %s already exists in the ai_classes" % class_name)

class AICore (object):
    """This forms the basis of an AI that runs a team."""
    
    def __init__(self, in_queue, out_queue):
        super(AICore, self).__init__()
        
        self.running = True
        self.team = None
        
        self.in_queue = in_queue
        self.out_queue = out_queue
        
        self.next_update = 0
        
        self.enemy_actors = []
        self.own_actors = []
        self.terrain = {}
        
        self.next_cycle = time.time()
        ai_lib.set_speed(self, 100)
        
        self.data_handlers = {
            "_default":     self._default_data_handler,
            "init":         self._init,
            "actors":       self._recieve_actors,
            "actor_types":  self._recieve_actor_types,
            "build_lists":  self._recieve_build_lists,
            "quit":         self._quit,
        }
        
        # Flags
        self.actors_updated = False
        
        self.prefs = {
            "actor_format": "list",
        }
    
    def read_queue(self):
        try:
            data = self.in_queue.get()
        except Exception as e:
            print("Error reading in from in_queue")
            raise
        
        cmd = data['cmd']
        del(data['cmd'])
        
        if cmd in self.data_handlers:
            try:
                self.data_handlers[cmd](**data)
            except Exception as e:
                raise
        else:
            self.data_handlers['_default'](cmd=cmd, **data)
    
    def _default_data_handler(self, **kwargs):
        raise Exception("No handler for cmd: %s" % kwargs['cmd'])
    
    def _quit(self):
        self.running = False
    
    def _init(self, **kwargs):
        if 'team' in kwargs:
            self.team = int(kwargs['team'])
    
    def _recieve_actors(self, actor_list):
        # This allows the AI to re-scan the lists and see if there's
        # anything it needs to do differently
        self.actors_updated = True
        
        if self.prefs['actor_format'] == "dict":
            return self._recieve_actors_as_dict(actor_list)
        
        self.enemy_actors = []
        self.own_actors = []
        
        for a in actor_list:
            if a.team == self.team:
                self.own_actors.append(a)
            else:
                self.enemy_actors.append(a)
    
    def _recieve_actors_as_dict(self, actor_list):
        self.enemy_actors = {}
        self.own_actors = {}
        
        for aid, a in actor_list.items():
            if a.team == self.team:
                self.own_actors[aid] = a
            else:
                self.enemy_actors[aid] = a
    
    def _recieve_actor_types(self, actor_types):
        self.actor_types = actor_types
    
    def _recieve_build_lists(self, build_lists):
        self.build_lists = build_lists
    
    def issue_orders(self, actor_id, cmd, pos=None, target=None):
        self.out_queue.put({
            "data_type":    "orders",
            "cmd":          cmd,
            "actor":        actor_id,
            "target":       target,
            "pos":          pos,
        })
        
        # Update our records so we don't spam the queue
        if type(self.own_actors) == list:
            for a in self.own_actors:
                if a.oid == actor_id:
                    a.current_order = cmd, pos, target
                    
                    if cmd == "build": a.build_queue.append(target)
        else:
            self.own_actors[actor_id].current_order = cmd, pos, target
            if cmd == "build": self.own_actors[actor_id].build_queue.append(target)
    
    def core_cycle(self):
        """The central loop for the AI"""
        
        # If there's stuff in the queue then we'll read it in
        while not self.in_queue.empty():
            self.read_queue()
        
        if time.time() > self.next_cycle:
            self.cycle()
    
    def cycle(self):
        """This is intended to be overwritten by the subclass"""
        pass

def _ai_process(ai_class, in_queue, out_queue):
    # Added to prevent memory leaks if the program doesn't
    # exit correctly
    start_time = time.time()
    time_to_live = 60 * 10# 10 Minutes
    
    try:
        a = ai_class(in_queue, out_queue)
        out_queue.put({"data_type":"prefs","prefs":a.prefs})
        time_to_live -= 1
        
        while a.running and time.time() - start_time < time_to_live:
            a.core_cycle()
        
    except KeyboardInterrupt as e:
        pass
    except Exception as e:
        raise

def make_ai(class_name):
    """Returns the ai in and out queues"""
    if class_name not in ai_classes:
        raise KeyError("No AI class by name of %s" % class_name)
    
    ai_in_queue = multiprocessing.Queue()
    ai_out_queue = multiprocessing.Queue()
    
    ai_class = ai_classes[class_name]
    
    p = multiprocessing.Process(target=_ai_process, args=(ai_class, ai_in_queue, ai_out_queue))
    p.start()
    
    return ai_in_queue, ai_out_queue

register_ai("basic", AICore)
