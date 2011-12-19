import pygame
from pygame.locals import *

import unittest

from sequtus.defaults import core
from sequtus.render import battle_screen
from sequtus.tests import application_t

BS = battle_screen.BattleScreen

class FakeSim (object):
    actors = {}
    def unselect_all_actors(self): pass

class BattleScreenTests(unittest.TestCase):
    def test_handle_active(self):
        s = BS(engine=core.temp_engine(), dimensions=[800, 600], fullscreen=False)
        s._handle_active(pygame.event.Event(ACTIVEEVENT))
        
        # pygame.event.Event(3, button=1, pos=(1, 1))
    
    def test_handle_keydown(self):
        s = BS(engine=core.temp_engine(), dimensions=[800, 600], fullscreen=False)
        event = pygame.event.Event(KEYDOWN, key=113)
        s._handle_keydown(event)
    
    def test_handle_keyhold(self):
        s = BS(engine=core.temp_engine(), dimensions=[800, 600], fullscreen=False)
        event = None
        s._handle_keyhold()
    
    def test_handle_keyup(self):
        s = BS(engine=core.temp_engine(), dimensions=[800, 600], fullscreen=False)
        event = pygame.event.Event(KEYUP, key=113)
        s._handle_keyup(event)

    def test_handle_mousemotion(self):
        s = BS(engine=core.temp_engine(), dimensions=[800, 600], fullscreen=False)
        event = None
        s._handle_mousemotion(event)

    def test_handle_mousedown(self):
        s = BS(engine=core.temp_engine(), dimensions=[800, 600], fullscreen=False)
        event = pygame.event.Event(MOUSEBUTTONDOWN, button=1, pos=(100,100))
        s._handle_mousedown(event)
    
    def test_handle_mouseup(self):
        s = BS(engine=core.temp_engine(), dimensions=[800, 600], fullscreen=False)
        s.sim = FakeSim()
        
        s.unselect_all_actors = lambda: 1
        
        # Left click
        s._handle_mouseup(pygame.event.Event(MOUSEBUTTONUP, button=1, pos=(100,100)))
        
        # Left click with a mouse mode
        s.mouse_mode = "move"
        s._handle_mouseup(pygame.event.Event(MOUSEBUTTONUP, button=1, pos=(100,100)))
        s.mouse_mode = None
        
        # Right click
        s._handle_mouseup(pygame.event.Event(MOUSEBUTTONUP, button=3, pos=(100,100)))

    def test_handle_mousedrag(self):
        s = BS(engine=core.temp_engine(), dimensions=[800, 600], fullscreen=False)
        event = pygame.event.Event(MOUSEMOTION, pos=(100,100))
        s._handle_mousedrag(event)
    
    def test_handle_mousedragup(self):
        s = BS(engine=core.temp_engine(), dimensions=[800, 600], fullscreen=False)
        event = pygame.event.Event(MOUSEBUTTONUP, button=1, pos=(100,100))
        s._handle_mousedragup(event)

    def test_handle_doubleclick(self):
        s = BS(engine=core.temp_engine(), dimensions=[800, 600], fullscreen=False)
        s.sim = FakeSim()
        
        first_click = pygame.event.Event(MOUSEBUTTONUP, button=1, pos=(80,80))
        second_click = pygame.event.Event(MOUSEBUTTONUP, button=1, pos=(100,100))
        
        s._handle_doubleclick(first_click, second_click)
    
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
        
        

suite = unittest.TestLoader().loadTestsFromTestCase(BattleScreenTests)
