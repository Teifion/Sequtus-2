from __future__ import division

import pygame

import math

def set_fps(screen, fps):
    return 1/fps

def get_max_window_size(self, preferred_size=None):
    """Takes the preferred size and gets the closest it can (rounding
    down to a smaller screen). It will always try to get the same ratio,
    if it cannot find the same ratio it will error."""
    
    # Default to max size!
    if preferred_size == None:
        return pygame.display.list_modes()[0]
    
    x, y = preferred_size
    ratio = x/y
    
    found_size = (0,0)
    for sx, sy in pygame.display.list_modes():
        sratio = sx/sy
        
        if sratio != ratio:
            continue
        
        # Make sure it's small enough
        if sx <= x and sy <= y:
            if sx > found_size[0] and sy > found_size[1]:
                found_size = sx, sy
    
    if found_size != (0,0):
        return found_size
    return None

def make_rotated_image(image, angle):
    return pygame.transform.rotate(image, -angle)

keyboards = {
    "colemak-qwerty": {
        "q": "q",
        "w": "w",
        "f": "e",
        "p": "r",
        "g": "t",
        "j": "y",
        "l": "u",
        "u": "i",
        "y": "o",
        ";": "p",
          
        "a": "a",
        "r": "s",
        "s": "d",
        "t": "f",
        "d": "g",
        "h": "h",
        "n": "j",
        "e": "k",
        "i": "l",
          
        "z": "z",
        "x": "x",
        "c": "c",
        "v": "v",
        "b": "b",
        "k": "n",
        "m": "m",
    }
}

# Make reverse dictionaries
keys = keyboards.keys()
for k in keys:
    a,b = k.split("-")
    new_key = "%s-%s" % (b,a)
    
    keyboards[new_key] = {}
    
    for k1, k2 in keyboards[k].items():
        keyboards[new_key][k2] = k1

    

def translate_keyboard(from_keyboard, to_keyboard, key):
    """User input is the from_keyboard, translating to the to_keyboard
    which we will then use."""
    
    d = "%s-%s" % (from_keyboard, to_keyboard)
    
    if d not in keyboards:
        raise KeyError("Keyboard mapping %s does not exist in the lookup table" % d)
    
    k = keyboards[d]
    
    # Lowercase first
    if key in k:
        return k[key]
    
    # It may be an uppercase character
    elif key.lower() in k:
        return k[key.lower()].upper()
    
    # Not in the list, it's assumed it matches the same
    return key


def _transition_fade_to_black(the_screen, total_frames=60):
    surf = the_screen.engine.display
    
    def trans(frame):
        if frame > total_frames:
            return None
        
        v = 255 - ((frame/total_frames) * 255)
        
        the_screen.background = (v, v, v)
        
        return True
    
    return trans

def _transition_fade_all_to_black(the_screen, total_frames=60):
    surf = the_screen.engine.display
    
    def trans(frame):
        if frame > total_frames:
            return None
        
        v = 255 - ((frame/total_frames) * 255)
        
        colour = (v, v, v)
        surf.fill(colour)
        
        return True
    
    return trans

transitions = {
    "Fade to black": _transition_fade_to_black,
    "Fade to all black": _transition_fade_all_to_black,
}

