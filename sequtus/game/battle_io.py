from __future__ import division

import time
import weakref

import pygame
from pygame.locals import *

from sequtus.render import screen
from sequtus.libs import screen_lib, actor_lib, vectors

class BattleIO (screen.Screen):
    """
    BattleIO expands the event handlers of the screen class for use in battle
    """
    
    def __init__(self, engine):
        super(BattleIO, self).__init__(engine, engine.screen_size)
    
    def add_order(self, the_actor, command, pos=None, target=None):
        """Sets the order for a given actor"""
        if type(the_actor) == int:
            the_actor = self.actors[the_actor]
        self.orders[self.tick + self.tick_jump].append((the_actor, command, pos, target))
    
    def queue_order(self, the_actor, command, pos=None, target=None):
        """Adds an order to the queue for a given actor"""
        if type(the_actor) == int:
            the_actor = self.actors[the_actor]
        self.q_orders[self.tick + self.tick_jump].append((the_actor, command, pos, target))
    
    def left_click_actor(self, act):
        """Invert selection on actor"""
        if act.selected:
            self.unselect_actor(act)
        else:
            self.select_actor(act)
    
    def double_left_click_actor(self, act):
        mods = pygame.key.get_mods()
        actors_to_select = []
        
        scr_rect = (
            -self.scroll_x + self.draw_area[0],
            -self.scroll_y + self.draw_area[1],
            -self.scroll_x + self.draw_area[2],
            -self.scroll_y + self.draw_area[3]
        )
        
        for aid, a in self.actors.items():
            if a.actor_type == act.actor_type:
                if actor_lib.is_inside(a, scr_rect):
                    actors_to_select.append(a)
        
        if KMOD_SHIFT & mods:
            # Add to current selection
            for a in actors_to_select:
                self.select_actor(a)
        else:
            self.selected_actors = []
            
            # Set as current selection
            for a in actors_to_select:
                self.select_actor(a)
        
        self._selection_has_changed = True
    

    
    def unselect_all_actors(self):
        for a in self.selected_actors[:]:
            del(self.selected_actors[self.selected_actors.index(a)])
            a.selected = False
            self._selection_has_changed = True
    
    def unselect_actor(self, a):
        try:
            a.selected = False
            del(self.selected_actors[self.selected_actors.index(a)])
        except Exception as e:
            print("""! battle_screen.unselect_actor had an exception trying
to delete an actor from the list of selected actors.""")
        
        a.selected = False
        self._selection_has_changed = True
    
    def select_actor(self, a):
        self.selected_actors.append(a)
        a.selected = True
        self._selection_has_changed = True
    
    def update(self):
        # It might be that the mouse is scrolling
        # but we only use this if there are no arrow keys held down
        if self.allow_mouse_scroll:
            if self.scroll_up_key not in self.keys_down:
                if self.scroll_down_key not in self.keys_down:
                    if self.scroll_right_key not in self.keys_down:
                        if self.scroll_left_key not in self.keys_down:
                            # None of our scroll keys are down, we can mouse scroll
                            self.check_mouse_scroll()
    
    def check_mouse_scroll(self):
        left_val = self.scroll_boundary - (self.engine.window_width - self.mouse[0])
        right_val = self.scroll_boundary - self.mouse[0]
        
        up_val = self.scroll_boundary - (self.engine.window_height - self.mouse[1])
        down_val = self.scroll_boundary - self.mouse[1]
        
        # Scroll based on how far it is
        if down_val > 0:
            self.scroll_down(down_val/self.scroll_boundary)
        elif up_val > 0:
            self.scroll_up(up_val/self.scroll_boundary)
        
        if left_val > 0:
            self.scroll_left(left_val/self.scroll_boundary)
        elif right_val > 0:
            self.scroll_right(right_val/self.scroll_boundary)
    
    def assign_control_group(self, key):
        self.control_groups[key] = self.selected_actors[:]
    
    def select_control_group(self, key):
        if len(self.control_groups[key]) > 0:
            self.unselect_all_actors()
            for a in self.control_groups[key][:]:
                self.select_actor(a)
            
            self._selection_has_changed = True
    
    def selection_changed(self):
        pass
    


