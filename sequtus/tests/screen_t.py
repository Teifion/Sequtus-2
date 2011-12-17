import pygame
from pygame.locals import *

import unittest

from sequtus.defaults import core
from sequtus.render import screen

class ScreenTests(unittest.TestCase):
    def test_innit(self):
        pygame.init()
        
        # This is just to make sure it'll actually load up
        s = screen.Screen(engine=core.temp_engine(), dimensions=[800, 600], fullscreen=False)
        s = screen.Screen(engine=core.temp_engine(), dimensions=[800, 600], fullscreen=True)
    
    def test_redraw(self):
        s = screen.Screen(engine=core.temp_engine(), dimensions=[800, 600], fullscreen=False)
        s.engine.display = pygame.Surface((1,1))# Fake a surface to draw on
        s.redraw()
    
    """
    Example events
    <Event(1-ActiveEvent {'state': 3, 'gain': 0})>
    <Event(2-KeyDown {'scancode': 12, 'key': 113, 'unicode': u'q', 'mod': 1024})>
    <Event(3-KeyUp {'scancode': 0, 'key': 310, 'mod': 0})>
    <Event(4-MouseMotion {'buttons': (0, 0, 0), 'pos': (291, 279), 'rel': (-1, 0)})>
    <Event(5-MouseButtonDown {'button': 5, 'pos': (291, 279)})>
    <Event(6-MouseButtonUp {'button': 1, 'pos': (292, 278)})>
    <Event(12-Quit {})>
    """
    
    def test_handle_active(self):
        s = screen.Screen(engine=core.temp_engine(), dimensions=[800, 600], fullscreen=False)
        s._handle_active(pygame.event.Event(ACTIVEEVENT))
        
        # pygame.event.Event(3, button=1, pos=(1, 1))
    
    def test_handle_keydown(self):
        s = screen.Screen(engine=core.temp_engine(), dimensions=[800, 600], fullscreen=False)
        event = pygame.event.Event(KEYDOWN, key=113)
        s._handle_keydown(event)
    
    def test_handle_keyhold(self):
        s = screen.Screen(engine=core.temp_engine(), dimensions=[800, 600], fullscreen=False)
        s._handle_keyhold()
    
    def test_handle_keyup(self):
        s = screen.Screen(engine=core.temp_engine(), dimensions=[800, 600], fullscreen=False)
        event = pygame.event.Event(KEYUP, key=113)
        s._handle_keyup(event)

    def test_handle_mousemotion(self):
        s = screen.Screen(engine=core.temp_engine(), dimensions=[800, 600], fullscreen=False)
        event = pygame.event.Event(MOUSEMOTION, pos=(100,100))
        s._handle_mousemotion(event)

    def test_handle_mousedown(self):
        s = screen.Screen(engine=core.temp_engine(), dimensions=[800, 600], fullscreen=False)
        event = pygame.event.Event(MOUSEBUTTONDOWN, button=1, pos=(100,100))
        s._handle_mousedown(event)
    
    def test_handle_mouseup(self):
        s = screen.Screen(engine=core.temp_engine(), dimensions=[800, 600], fullscreen=False)
        s._handle_mouseup(pygame.event.Event(MOUSEBUTTONUP, button=1, pos=(100,100)))

    def test_handle_mousedrag(self):
        s = screen.Screen(engine=core.temp_engine(), dimensions=[800, 600], fullscreen=False)
        event = pygame.event.Event(MOUSEMOTION, pos=(100,100))
        s._handle_mousedrag(event)
    
    def test_handle_mousedragup(self):
        s = screen.Screen(engine=core.temp_engine(), dimensions=[800, 600], fullscreen=False)
        event = pygame.event.Event(MOUSEBUTTONUP, button=1, pos=(100,100))
        s._handle_mousedragup(event)

    def test_handle_doubleclick(self):
        s = screen.Screen(engine=core.temp_engine(), dimensions=[800, 600], fullscreen=False)
        first_click = pygame.event.Event(MOUSEBUTTONUP, button=1, pos=(80,80))
        second_click = pygame.event.Event(MOUSEBUTTONUP, button=1, pos=(100,100))
        s._handle_doubleclick(first_click, second_click)

suite = unittest.TestLoader().loadTestsFromTestCase(ScreenTests)
