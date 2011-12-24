from __future__ import division
import pygame
import math
import vectors

def _convert(r):
    # Takes a pos, pos, size, size rect and returns a pos, pos, pos, pos rect
    return (r[0], r[1], r[2] + r[0], r[3] + r[1])

# 2D Function
def rect_collision(r1, r2, convert=False):
    """
    r1 and r2 are 4 length sequences of (left, top, right, bottom)
    or at least something that can be used as such.
    
    If the convert flag is set then the function assumes the rects are
    position and size and converts them to position and position pairs.
    """
    
    if convert:
        if type(r1) == tuple or type(r1) == list:
            r1 = _convert(r1)
        else:
            r1 = (r1.left, r1.top, r1.right, r1.bottom)
        
        if type(r2) == tuple or type(r2) == list:
            r2 = _convert(r2)
        else:
            r2 = (r2.left, r2.top, r2.right, r2.bottom)
    
    left1, top1, right1, bottom1 = r1
    left2, top2, right2, bottom2 = r2
    
    # Horrizontal
    if right1 < left2: return False
    if left1 > right2: return False
    
    # Vertical
    if bottom1 < top2: return False
    if top1 > bottom2: return False
    
    return True

