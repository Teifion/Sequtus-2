from __future__ import division
import pygame
from pygame.locals import *

from sequtus.libs import vectors

class ObjectBase (object):
    """Actors, bullets and any other active object in the game inherits
    from this class"""
    ai_update_time = 100
    
    image               = ""
    flags               = []
    size                = (0,0)
    
    def __init__(self):
        super(ObjectBase, self).__init__()
        
        self.pos        = vectors.V([-100, -100, 0])# Assume we're offscreen
        self.velocity   = vectors.V([0,0,0])
        self.facing     = [0,0]# XY, Z
        
        self.oid = 0
    
    # These allow us to order actors based on their aid
    def __lt__(self, other): return self.oid < other.oid
    def __gt__(self, other): return self.oid > other.oid
    
    def contains_point(self, point):
        """Point is a length 2 sequence X, Y"""
        left = self.pos[0] - self.rect.width/2
        right = self.pos[0] + self.rect.width/2
        
        top = self.pos[1] - self.rect.height/2
        bottom = self.pos[1] + self.rect.height/2
        
        if left <= point[0] <= right:
            if top <= point[1] <= bottom:
                return True
    
    def new_image(self, img):
        self.image = img
        self.rect = self.image.get_rect()

    def update(self):
        self.pos += self.velocity
        
        # Set rect
        self.rect.topleft = (
            self.pos[0] - self.rect.width/2,
            self.pos[1] - self.rect.height/2
        )
    
