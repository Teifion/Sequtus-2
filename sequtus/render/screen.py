from __future__ import division

import time

import pygame
from pygame.locals import *

from sequtus.libs import screen_lib

class Screen (object):
    """
    The Screen class handles the basic rendering of the screen and transitions
    between windowed mode and full screen mode. It also provides the base
    level reading of events (keys, mouse etc).
    """
    
    def __init__(self, engine, dimensions=None, fullscreen=False):
        super(Screen, self).__init__()
        
        # Handles
        self.engine = engine
        self.size = dimensions
        self.fullscreen = fullscreen
        
        if dimensions == None:
            self.fullscreen = True
        
        # Empty holders
        self.controls = {}
        
        # This is the title drawn at the top of the window
        self.name = ""
        
        # FPS (redraw rate)
        self._next_redraw = 0
        self._redraw_delay = 1/engine.fps
        
        # Saved variables
        self.mouse_is_down = False
        self.keys_down = {}
        self.true_mousedown_at = None
        self.scrolled_mousedown_at = None
        self.true_mousedrag_at = None
        self.scrolled_mousedrag_at = None
        self.scroll_at_mousedown = None
        self.scroll_x, self.scroll_y = 0, 0# Current location scrolled to
        
        # If image == None the colour is used instead
        self.background_image   = None
        self.background_colour  = (200, 200, 200)# Default to a grey background
        
        # Used for working out double click stuff
        self._last_mouseup = [None, -1]
        self._double_click_interval = 0.25
        
        # Transitions
        self.transition = None
        self.transition_frame = -1
        self.on_transition = None
        self.on_transition_kwargs = None
        
        if self.fullscreen:
            self.switch_to_fullscreen()
    
    def begin_transition(self, mode, callback, kwargs={}, trans_kwargs={}):
        self.on_transition = callback
        self.on_transition_kwargs = {}
        
        self.transition = screen_lib.transitions[mode](self, **trans_kwargs)
    
    def activate(self, **kwargs):
        """Called when activated after a screen change"""
        if self.fullscreen:
            self.switch_to_fullscreen()
        else:
            self.switch_to_windowed()
        
        pygame.display.set_caption(self.name)
    
    def get_rotated_image(self, image_name, angle=0):
        return pygame.transform.rotate(self.engine.images[image_name], -angle)
    
    def _redraw(self):
        """Wrapper around redraw to not draw too fast"""
        if time.time() < self._next_redraw: return
        self.redraw()
        self._next_redraw = time.time() + self._redraw_delay
    
    def _update(self):
        # Does nothing but need it here for battle_screen to subclass
        pass
        
        """Wrapper around update to not update too fast"""
        if time.time() < self._next_update: return
        self.update()
        self._next_update = time.time() + self._update_delay
    
    def redraw(self):
        """Basic screens do not have scrolling capabilities
        you'd need to use a subclass for that"""
        surface = self.engine.display
        
        # Default the background to a solid colour
        if self.background_image == None:
            surface.fill(self.background_colour)
        else:
            self.background = self.background_image.copy()
            surface.blit(self.background, pygame.Rect(0, 0, self.size[0], self.size[1]))
        
        self.draw_controls()
        self.draw_transition()
        self.post_redraw()
        
        pygame.display.flip()
    
    def post_redraw(self):
        """Allows us to append functionality to the redraw function"""
        pass
    
    def draw_controls(self):
        surface = self.engine.display
        
        to_kill = []
        
        # We use all of this to draw the controls in order
        # of priority (high priority goes at the top of the screen)
        priorities = set()
        control_sets = {}
        for i, c in self.controls.items():
            if c.kill:
                to_kill.append(i)
                continue
            
            p = c.draw_priority
            if p not in control_sets: control_sets[p] = []
            
            control_sets[p].append(i)
            priorities.add(c.draw_priority)
        
        for k in to_kill:
            del(self.controls[k])
        
        priorities = list(priorities)
        priorities.sort()
        
        for p in priorities:
            for i in control_sets[p]:
                c = self.controls[i]
                if c.visible:
                    c.update()
                    if c.blit_image:
                        surface.blit(*c.image())
                    else:
                        c.draw(surface)
    
    def draw_transition(self):
        if self.transition != None:
            self.transition_frame += 1
            r = self.transition(self.transition_frame)
            
            if r == None:
                self.on_transition(*self.on_transition_args, **self.on_transition_kwargs)
                return
    
    # Event handlers
    # Internal version allows us to sub-class without requiring a super call
    # makes the subclass cleaner
    def _handle_active(self, event):
        self.handle_active(event)
    
    # Keyboard
    def _handle_keydown(self, event):
        self.keys_down[event.key] = time.time()
        self.test_for_keyboard_commands()
        self.handle_keydown(event)
    
    def _handle_keyhold(self):
        if len(self.keys_down) > 0:
            self.handle_keyhold()
    
    def _handle_keyup(self, event):
        if event.key in self.keys_down:
            del(self.keys_down[event.key])
        self.handle_keyup(event)
    
    # Mouse
    def _handle_mousedown(self, event):
        self.mouse_is_down = True
        self.true_mousedown_at = event.pos[:]
        self.scroll_at_mousedown = self.scroll_x, self.scroll_y
        
        self.scrolled_mousedown_at = (
            event.pos[0] + self.scroll_x,
            event.pos[1] + self.scroll_y
        )
        
        for i, c in self.controls.items():
            if c.contains(event.pos):
                # If it's in a control we don't want to allow a drag option
                self.scrolled_mousedown_at = None
                
                if c.accepts_mousedown:
                    try:
                        c.handle_mousedown(event, *c.mousedown_args, **c.mousedown_kwargs)
                    except Exception as e:
                        print("Func: %s" % c.handle_mousedown)
                        print("Event: %s" % event)
                        print("Args: %s" % c.mousedown_args)
                        print("Kwargs: %s" % c.mousedown_kwargs)
                        raise
        
        self.mouse_is_down = True
        self.handle_mousedown(event)
    
    def _handle_mouseup(self, event):
        self.mouse_is_down = False
        
        # If it's been less than X seconds since the last click
        # then it is a double click
        if time.time() <= self._last_mouseup[1] + self._double_click_interval:
            return self._handle_doubleclick(self._last_mouseup[0], event)
        
        # Save this incase it's the first part of a double click
        self._last_mouseup = [event, time.time()]
        
        for i, c in self.controls.items():
            if c.accepts_mouseup:
                if c.contains(event.pos):
                    try:
                        c.handle_mouseup(event, *c.mouseup_args, **c.mouseup_kwargs)
                    except Exception as e:
                        print("Func: %s" % c.handle_mouseup)
                        print("Event: %s" % event)
                        print("Args: %s" % c.mouseup_args)
                        print("Kwargs: %s" % c.mouseup_kwargs)
                        raise
        
        self.mouse_is_down = False
        
        # If the mouseup is the same as when it went down, it's just
        # a normal mouseup. If the down and up are different then it's
        # the end of a drag
        scrolled_mouse_pos = (
            event.pos[0] + self.scroll_x,
            event.pos[1] + self.scroll_y
        )
        
        if scrolled_mouse_pos == self.scrolled_mousedown_at:
            self.handle_mouseup(event, drag=False)
        else:
            # TODO possibly add distance calc in, if it's just 1 pix then is
            # it really a mouse drag?
            self._handle_mousedragup(event)
            self.handle_mouseup(event, drag=True)
        
    
    def _handle_doubleclick(self, first_click, second_click):
        for i, c in self.controls.items():
            if c.accepts_doubleclick:
                if c.contains(second_click.pos):
                    try:
                        c.handle_doubleclick(second_click, *c.mouseup_args, **c.mouseup_kwargs)
                    except Exception as e:
                        print("Func: %s" % c.handle_mouseup)
                        print("Event: %s" % second_click)
                        print("Args: %s" % c.mouseup_args)
                        print("Kwargs: %s" % c.mouseup_kwargs)
                        raise
        
        self.mouse_is_down = False
        self.handle_doubleclick(first_click, second_click)
    
    def _handle_mousemotion(self, event):
        # It's possibly this should be a mouse drag
        if self.mouse_is_down:
            self._handle_mousedrag(event)
        else:
            self.handle_mousemotion(event)
    
    def _handle_mousedrag(self, event):
        scrolled_mouse_pos = (event.pos[0] + self.scroll_x, event.pos[1] + self.scroll_y)
        self.true_mousedrag_at = event.pos[:]
        self.scrolled_mousedrag_at = scrolled_mouse_pos
        
        if self.scrolled_mousedown_at == None:
            return self.handle_mousedrag(event, None)
        else:
            # If dragging started within a control it may want to know
            for i, c in self.controls.items():
                if c.contains(self.true_mousedown_at):
                    c.handle_mousedrag(event)
                return
        
        drag_rect = (
            min(self.scrolled_mousedown_at[0], scrolled_mouse_pos[0]),
            min(self.scrolled_mousedown_at[1], scrolled_mouse_pos[1]),
            max(self.scrolled_mousedown_at[0], scrolled_mouse_pos[0]),
            max(self.scrolled_mousedown_at[1], scrolled_mouse_pos[1]),
        )
        self.handle_mousedrag(event, drag_rect)
    
    def _handle_mousedragup(self, event):
        if self.scrolled_mousedown_at == None:
            return self.handle_mousedragup(event, None)
        
        scrolled_mouse_pos = (
            event.pos[0] + self.scroll_x,
            event.pos[1] + self.scroll_y
        )
        
        drag_rect = (
            min(self.scrolled_mousedown_at[0], scrolled_mouse_pos[0]),
            min(self.scrolled_mousedown_at[1], scrolled_mouse_pos[1]),
            max(self.scrolled_mousedown_at[0], scrolled_mouse_pos[0]),
            max(self.scrolled_mousedown_at[1], scrolled_mouse_pos[1]),
        )
        self.handle_mousedragup(event, drag_rect)
    
    def quit(self, event=None):
        self.engine.quit()
    
    def test_for_keyboard_commands(self):
        # TODO Find a way to non-hard code it
        # TODO Find a way to make it work with Widows and Linux shortcuts
        # Cmd + Q
        if 113 in self.keys_down and 310 in self.keys_down:
            if self.keys_down[310] <= self.keys_down[113]:# Cmd has to be pushed first
                self.quit()
    
    def switch_to_fullscreen(self):
        self.fullscreen = True
        
        dimensions = screen_lib.get_max_window_size(self.size)
        
        # TODO work out if it's okay to use the HWSURFACE flag
        # or if I need to stick wih FULLSCREEN
        self.engine.display = pygame.display.set_mode(self.size, FULLSCREEN)
    
    def switch_to_windowed(self):
        self.fullscreen = False
        
        self.engine.display = pygame.display.set_mode(self.size)
    
    # Functions to subclass
    def handle_active(self, event): pass
    
    def handle_keydown(self, event): pass
    def handle_keyhold(self): pass
    def handle_keyup(self, event): pass
    
    def handle_mousemotion(self, event): pass
    
    def handle_mousedown(self, event): pass
    def handle_mouseup(self, event, drag=False): pass
    
    def handle_mousedrag(self, event, drag_rect): pass
    def handle_mousedragup(self, event, drag_rect): pass
    
    def handle_doubleclick(self, first_click, second_click): pass


