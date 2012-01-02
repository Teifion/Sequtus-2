from __future__ import division

import sys
import time
import math
import traceback
import re

import pygame
from pygame.locals import *

from sequtus.libs import vectors

root_path = re.compile(r"(.*/)?[a-zA-Z_]*\.py")
file_name = re.compile(r".*/(.*?)\.[a-zA-Z]*")

class EngineV4 (object):
    fps = 30# Frames per second
    cps = 30# Cycles per second (the running speed of the game)
    
    def __init__(self):
        super(EngineV4, self).__init__()
        
        # Get pygame going
        pygame.init()
        
        # Constructors for the screen we can use
        self.screens = {}
        
        # A reference to the current screen
        self.current_screen = None
        
        # Image cache
        self.images = {}
    
    def quit(self, event=None):
        """Close everything down"""
        pygame.quit()
        sys.exit()
    
    def set_screen(self, s, *args, **kwargs):
        """You can pass this either the name of a screen in the dict
        or a new instance of a screen.
        
        If passed the name you can also pass constructor arguments but these
        will only be used if it's a screen constructor."""
        
        if s in self.screens:
            s = self.screens[s]
        
        # It's a string but not in our dictionary
        elif type(s) == str:
            raise KeyError("Screen '%s' not found in screen dictionary" % s)
        
        # And launch
        self.current_screen = s
        self.current_screen.activate(*args, **kwargs)
        self.current_screen.redraw()
    
    # Contains main execution loop
    def start(self, screen, **kwargs):
        """
        This starts everything going. The screen argument is passed straight to set_screen.
        """
        try:
            self.startup()
            self.set_screen(screen, **kwargs)
            
            while True:
                for event in pygame.event.get():# Event handlers
                    if event.type == ACTIVEEVENT:       self.current_screen._handle_active(event)
                    if event.type == KEYDOWN:           self.current_screen._handle_keydown(event)
                    if event.type == KEYUP:             self.current_screen._handle_keyup(event)
                    if event.type == MOUSEBUTTONUP:     self.current_screen._handle_mouseup(event)
                    if event.type == MOUSEBUTTONDOWN:   self.current_screen._handle_mousedown(event)
                    if event.type == MOUSEMOTION:       self.current_screen._handle_mousemotion(event)
                    if event.type == QUIT:              self.current_screen.quit(event)
                
                # Check to see if a key has been held down
                self.current_screen._handle_keyhold()
                
                # Update and redraw calls
                self.current_screen._update()
                self.current_screen._redraw()
            
            # If anything goes wrong we want to try to kill pygame gracefully
        except Exception as e:
            traceback.print_exc(file=sys.stdout)
            
            if self.current_screen != None:
                self.current_screen.quit()
            
            pygame.quit()
            raise
        
        self.quit()
    
    def load_static_images(self, *images):
        """Loads a set of static images into the cache. It can be a list of
        file locations but can also accept length 2 tuples of key and location
        combos. e.g.
        
        load_static_images('bullet.png', 'tank.png')
        load_static_images(
            ['bullet', 'bullet.png'],
            ['tank', 'tank.png'])
        """
        
        # It's possible this isn't being run from the main directory
        # we thus need to make it a relative path
        regex_result = root_path.search(sys.argv[0])
        
        root = None
        if regex_result != None:
            root = regex_result.groups()[0]
        
        if root == None:
            root = ""
        
        for i in images:
            # Name and Location
            if type(i) == list:
                name, file_location = i
                file_location = "{}{}".format(root, file_location)
                self.images[name] = pygame.image.load(file_location)
            
            # Just location
            else:
                file_location = "{}{}".format(root, i)
                name = file_name.search(file_location).groups()[0]
                self.images[name] = pygame.image.load(file_location)
    
    def get_image(self, image_name, frame=0):
        """Wrapper for accessing both images and animations. Currently
        animations are not active so we just return the image."""
        return self.images[image_name]
        
        if type(self.images[image_name]) == pygame.Surface:
            return self.images[image_name]
        else:
            raise Exception("No handler for type %s" % type(self.images[image_name]))
    
    # Functions for sublcassing
    def startup(self):
        """Called when the application starts up"""
        pass
        

'''
class Animation (object):
    """An object that takes a picture and cuts it up into separate frames
    so that we can animate certain objects"""
    
    def __init__(self, filepath, columns=1, rows=1, animation_rate = 0.5, rotate_about=None):
        super(Animation, self).__init__()
        
        if columns < 1:
            raise Exception("Cannot have fewer than 1 column in an animation")
        
        if rows < 1:
            raise Exception("Cannot have fewer than 1 row in an animation")
        
        self.images = []
        self.animation_rate = animation_rate
        
        img = pygame.image.load(filepath)
        r = img.get_rect()
        
        # Break it down into tiles, save the tiles
        tile_width = r.width / columns
        tile_height = r.height / rows
        
        for y in range(rows):
            for x in range(columns):
                tile = pygame.Surface((tile_width, tile_height), SRCALPHA)
                tile.blit(img, (0,0), (x * tile_width, y * tile_height, tile_width, tile_height))
                
                self.images.append(tile)
        
        # Default the rotate about point
        if rotate_about == None:
            rotate_about = 0, 0, 0
        
        # centre_offset is a distance and angle
        self.centre_offset = (
            vectors.distance(rotate_about),
            vectors.angle(rotate_about),
        )
    
    def get_rect(self):
        return self.images[0].get_rect()
    
    def get_rotated_offset(self, angle):
        if self.centre_offset == (0, 0):
            return 0, 0
        
        # Get the actual angle to use
        offset_angle = vectors.bound_angle(
            vectors.add_vectors(self.centre_offset[1], angle)
        )
        
        return vectors.move_to_vector(offset_angle, self.centre_offset[0])
        
    
    def real_frame(self, frame):
        """If the frame count is too high, we need to bring it back
        to the correct number"""
        return frame % len(self.images)
    
    def get(self, img_number=0):
        img_number = int(math.floor(self.animation_rate * img_number))
        img_number = self.real_frame(img_number)
        
        return self.images[img_number]
    
    def __getitem__(self, key):
        if key in self.images: return self.images[key]
        return self.get(key)
'''

