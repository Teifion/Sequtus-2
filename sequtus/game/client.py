from __future__ import division

from sequtus.PodSixNet.Connection import connection, ConnectionListener

skip_set = ('issue_order', 'socketConnect', 'player_number')

class Client (ConnectionListener):
    def __init__(self, sim, address, port, debug=False):
        super(Client, self).__init__()
        self.sim = sim
        self.debug = debug
        self.Connect((address, port))
    
    def Send(self, *args, **kwargs):
        if self.debug:
            print(args[0])#, kwargs)
        
        super(Client, self).Send(*args, **kwargs)
    
    def quit(self, event=None):
        self.running = False
        connection.Send({'action': 'quit'})
    
    def Network(self, data):
        if data['action'] not in skip_set:
            action = data['action']
            del(data['action'])
            print("Client unhandled %s: %s" % (action, str(data)))
    
    def Network_other(self, data):
        raise Exception("")
    
    def Network_player_number(self, data):
        self.sim.player = data['number']
    
    def Network_error(self, data):
        raise Exception("%s, source: %s" % (data['error'], data['source']))
    
    def Network_issue_order(self, data):
        if self.debug:
            print(data)
        self.sim._real_issue_order(tick=data['tick'], actor_id=data['actor'], command=data['cmd'], pos=data['pos'], target=data['pos'])
    
    def Network_queue_order(self, data):
        self.sim._real_queue_order(tick=data['tick'], actor_id=data['actor'], command=data['cmd'], pos=data['pos'], target=data['pos'])
    
    def update(self):
        connection.Pump()
        self.Pump()
