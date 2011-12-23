import pygame
from pygame.locals import *

import unittest

from sequtus.defaults import core
from sequtus.render import battle_screen
from sequtus.tests import application_t

class BattleScreenTests(unittest.TestCase):
    def test_handle_active(self):
        with application_t.TestCore() as c:
            c.current_screen._handle_active(pygame.event.Event(ACTIVEEVENT))
    
    def test_handle_keydown(self):
        with application_t.TestCore() as c:
            event = pygame.event.Event(KEYDOWN, key=113)
            c.current_screen._handle_keydown(event)
    
    def test_handle_keyhold(self):
        with application_t.TestCore() as c:
            event = None
            c.current_screen._handle_keyhold()
    
    def test_handle_keyup(self):
        with application_t.TestCore() as c:
            event = pygame.event.Event(KEYUP, key=113)
            c.current_screen._handle_keyup(event)

    def test_handle_mousemotion(self):
        with application_t.TestCore() as c:
            event = None
            c.current_screen._handle_mousemotion(event)

    def test_handle_mousedown(self):
        with application_t.TestCore() as c:
            event = pygame.event.Event(MOUSEBUTTONDOWN, button=1, pos=(100,100))
            c.current_screen._handle_mousedown(event)
    
    def test_handle_mouseup(self):
        with application_t.TestCore() as c:
            c.current_screen.unselect_all_actors = lambda: 1
            
            # Left click
            c.current_screen._handle_mouseup(pygame.event.Event(MOUSEBUTTONUP, button=1, pos=(500,500)))
            
            # Left click with a mouse mode
            c.current_screen.mouse_mode = "move"
            c.current_screen._handle_mouseup(pygame.event.Event(MOUSEBUTTONUP, button=1, pos=(500,500)))
        
            # Right click
            c.current_screen.mouse_mode = None
            c.current_screen._handle_mouseup(pygame.event.Event(MOUSEBUTTONUP, button=3, pos=(500,500)))

    def test_handle_mousedrag(self):
        with application_t.TestCore() as c:
            event = pygame.event.Event(MOUSEMOTION, pos=(100,100))
            c.current_screen._handle_mousedrag(event)
    
    def test_handle_mousedragup(self):
        with application_t.TestCore() as c:
            event = pygame.event.Event(MOUSEBUTTONUP, button=1, pos=(100,100))
            c.current_screen._handle_mousedragup(event)

    def test_handle_doubleclick(self):
        with application_t.TestCore() as c:
            first_click = pygame.event.Event(MOUSEBUTTONUP, button=1, pos=(500, 500))
            second_click = pygame.event.Event(MOUSEBUTTONUP, button=1, pos=(500, 500))
        
            c.current_screen._handle_doubleclick(first_click, second_click)
    
    def test_doubleclick_actor(self):
        with application_t.TestCore() as c:
            first_click = pygame.event.Event(MOUSEBUTTONUP, button=1, pos=(94, 120))
            second_click = pygame.event.Event(MOUSEBUTTONUP, button=1, pos=(94, 120))
            
            c.current_screen._handle_doubleclick(first_click, second_click)
    
    def test_click_actor(self):
        # Left click
        with application_t.TestCore() as c:
            self.assertEqual(0, len(c.current_screen.selected_actors))
            c.current_screen._handle_mousedown(pygame.event.Event(MOUSEBUTTONDOWN, button=1, pos=(94, 120)))
            c.current_screen._handle_mouseup(pygame.event.Event(MOUSEBUTTONUP, button=1, pos=(94, 120)))
            self.assertEqual(1, len(c.current_screen.selected_actors))
            
        # Left click miss
        with application_t.TestCore() as c:
            self.assertEqual(0, len(c.current_screen.selected_actors))
            c.current_screen._handle_mousedown(pygame.event.Event(MOUSEBUTTONDOWN, button=1, pos=(1194, 1120)))
            c.current_screen._handle_mouseup(pygame.event.Event(MOUSEBUTTONUP, button=1, pos=(1194, 1120)))
            self.assertEqual(0, len(c.current_screen.selected_actors))
        
        # Right click
        with application_t.TestCore() as c:
            self.assertEqual(0, len(c.current_screen.selected_actors))
            c.current_screen._handle_mousedown(pygame.event.Event(MOUSEBUTTONDOWN, button=3, pos=(94, 120)))
            c.current_screen._handle_mouseup(pygame.event.Event(MOUSEBUTTONUP, button=3, pos=(94, 120)))
            self.assertEqual(0, len(c.current_screen.selected_actors))
        
        # Right click miss
        with application_t.TestCore() as c:
            self.assertEqual(0, len(c.current_screen.selected_actors))
            c.current_screen._handle_mousedown(pygame.event.Event(MOUSEBUTTONDOWN, button=3, pos=(1194, 1120)))
            c.current_screen._handle_mouseup(pygame.event.Event(MOUSEBUTTONUP, button=3, pos=(1194, 1120)))
            self.assertEqual(0, len(c.current_screen.selected_actors))
        
        # Drag
        with application_t.TestCore() as c:
            self.assertEqual(0, len(c.current_screen.selected_actors))
            c.current_screen._handle_mousedown(pygame.event.Event(MOUSEBUTTONDOWN, button=1, pos=(10, 10)))
            c.current_screen._handle_mousemotion(pygame.event.Event(MOUSEMOTION, button=1, pos=(20, 20)))
            c.current_screen._handle_mouseup(pygame.event.Event(MOUSEBUTTONUP, button=1, pos=(100, 100)))
            self.assertEqual(1, len(c.current_screen.selected_actors))
        
        # Drag miss
        with application_t.TestCore() as c:
            self.assertEqual(0, len(c.current_screen.selected_actors))
            c.current_screen._handle_mousedown(pygame.event.Event(MOUSEBUTTONDOWN, button=1, pos=(1000, 1000)))
            c.current_screen._handle_mousemotion(pygame.event.Event(MOUSEMOTION, button=1, pos=(2000, 2000)))
            c.current_screen._handle_mouseup(pygame.event.Event(MOUSEBUTTONUP, button=1, pos=(3000, 3000)))
            self.assertEqual(0, len(c.current_screen.selected_actors))
    
    def test_selection_and_unselection(self):
        with application_t.TestCore() as c:
            # Using integers/oids
            self.assertEqual(0, len(c.current_screen.selected_actors))
            c.current_screen.select_actor(0)
            self.assertEqual(1, len(c.current_screen.selected_actors))
            c.current_screen.unselect_actor(0)
            self.assertEqual(0, len(c.current_screen.selected_actors))
            
            # Unsellect all
            c.current_screen.select_actor(0)
            c.current_screen.unselect_all_actors()
            self.assertEqual(0, len(c.current_screen.selected_actors))
            
            # Get index first, then get reference
            index = c.current_screen.sim.actors.keys()[0]
            first_actor = c.current_screen.sim.actors[index]
            
            # Using direct references
            c.current_screen.select_actor(first_actor)
            self.assertEqual(1, len(c.current_screen.selected_actors))
            c.current_screen.unselect_actor(first_actor)
            self.assertEqual(0, len(c.current_screen.selected_actors))
    
    def test_calling_of_order(self):
        with application_t.TestCore() as c:
            data_holder = {}
            def _f(self, *args, **kwargs):
                data_holder['args'] = args
                data_holder['kwargs'] = kwargs
            
            # Move
            c.current_screen.select_actor(0)
            c.current_screen.sim.add_order = _f
            
            c.current_screen._handle_mousedown(pygame.event.Event(MOUSEBUTTONDOWN, button=3, pos=(1194, 1120)))
            c.current_screen._handle_mouseup(pygame.event.Event(MOUSEBUTTONUP, button=3, pos=(1194, 1120)))
            
            self.assertEqual(data_holder, {
                "args":     ("move",),
                "kwargs":   {"pos": (1194, 1120)}
            })
            
            # Now test it is queued
            data_holder = {}
            c.current_screen.unselect_all_actors()
            c.current_screen.select_actor(0)
            c.current_screen.sim.queue_order = _f
            
            pygame.key.set_mods(KMOD_SHIFT)
            mods = pygame.key.get_mods()
            
            c.current_screen._handle_mousedown(pygame.event.Event(MOUSEBUTTONDOWN, button=3, pos=(1194, 1120)))
            c.current_screen._handle_mouseup(pygame.event.Event(MOUSEBUTTONUP, button=3, pos=(1194, 1120)))
            
            # TODO Shift isn't detected as held down so it doesn't work correctly
            # self.assertEqual(data_holder, {
            #     "args":     ("move",),
            #     "kwargs":   {"pos": (1194, 1120)}
            # })
            
            
            # Left click, no order should be sent
            data_holder = {}
            c.current_screen.unselect_all_actors()
            c.current_screen.select_actor(0)
            c.current_screen.sim.add_order = _f
            
            c.current_screen._handle_mousedown(pygame.event.Event(MOUSEBUTTONDOWN, button=1, pos=(1194, 1120)))
            c.current_screen._handle_mouseup(pygame.event.Event(MOUSEBUTTONUP, button=1, pos=(1194, 1120)))
            
            self.assertEqual(data_holder, {})
    
            
        
        

suite = unittest.TestLoader().loadTestsFromTestCase(BattleScreenTests)
