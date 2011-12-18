from __future__ import division

import time
import weakref

import pygame
from pygame.locals import *

from sequtus.render import screen
from sequtus.libs import screen_lib, actor_lib, vectors

NUMBERS = range(K_0, K_9+1)

class BattleScreen (screen.Screen):
    """BattleScreen is the same as a normal screen except it handles things
    such as drawing actors etc. Any simulation takes place in the sim not in
    the screen.
    
    BattleScreen is responsible for user-computer IO (keyboard, mouse) but not
    for any networking."""
    
    def __init__(self, engine, dimensions=None, fullscreen=False, sim=None):
        super(BattleScreen, self).__init__(engine, dimensions, fullscreen)
        
        # The sim is where all the action takes place, the screen reads
        # information from this to display, the only information the screen
        # sends the sim are orders
        self.sim = sim
        
        # This is used to work out what size rectangle to draw to for the
        # battlefield (so taking into account controls and menus)
        self.draw_area = [0, 0, dimensions[0], dimensions[1]]
        
        # Draw offset is the amount we must offset anything to take into
        # account scrolling and controls along the top and bottom.
        self.draw_offset = [0, 0]
        
        # Ctrl + # to assign, # to select
        self.control_groups = {}
        for i in NUMBERS:
            self.control_groups[i] = []
        
        # M for move, A for attack etc
        self.hotkeys = {}
        
        self.scroll_up_key = K_UP
        self.scroll_down_key = K_DOWN
        self.scroll_right_key = K_RIGHT
        self.scroll_left_key = K_LEFT
        
        # Defines how far we can scroll in any direction
        # Generally you'll want to have max-x to be the width of background
        # minus width of window and same for max-y but with height
        self.scroll_boundaries = (0, 0, 1000-640, 1000-480)
        
        self.scroll_speed = 15
        self.allow_mouse_scroll = False
        self.have_scrolled = False
        
        # Mouse callbacks
        self.mouseup_callback = None
        self.mouseup_callback_kwargs = {}
        self.mouse_mode = None
        
        # These allow us to limit scrolling frequency
        self._next_scroll = 0
        self.scroll_delay = 0.01
        
        # place_image is used to show the potential location of
        # a building
        self.place_image = None
        
        # Each actor gets it's own ID
        self._current_actor_id = 0
        
        # This is flagged instead of a function call because it's possible
        # that we may alter the selection several times in a row and it would
        # be a waste to rebuild menus several times
        self._selection_has_changed = False
        self.selected_actors = []
    
    def activate(self):
        super(BattleScreen, self).activate()
        self.draw_area[2] = self.size[0] - self.draw_area[0]
        self.draw_area[3] = self.size[1] - self.draw_area[1]
    
    def quit(self):
        self.sim.quit()
        super(BattleScreen, self).quit()
    
    def _update(self):
        self.sim._update()
    
    def redraw(self):
        """Overrides the basic redraw as it's intended to be used with more
        animation and actors etc."""
        
        # If selection has changed then we may want to update some stuff
        if self._selection_has_changed:
            self.selection_changed()
            self._selection_has_changed = False
        
        surface = self.engine.display
        
        # Draw background taking into account scroll
        if self.background_image != None:
            surface.blit(
                self.background_image,
                pygame.Rect(self.draw_area),
                pygame.Rect(
                    self.scroll_x,
                    self.scroll_y,
                    self.draw_area[2],
                    self.draw_area[3]),
            )
        else:
            surface.fill(self.background_colour)
        
        # Actors
        for aid, a in self.sim.actors.items():
            a.frame += 1
            
            actor_img = screen_lib.make_rotated_image(
                image = self.engine.get_image(a.image, a.frame),
                angle = a.facing[0]
            )
            
            # Get the actor's image and rectangle
            # actor_img = self.image_cache[img_name]
            r = pygame.Rect(actor_img.get_rect())
            r.left = a.pos[0] - self.draw_offset[0] - r.width/2
            r.top = a.pos[1] - self.draw_offset[1] - r.height/2
            
            # Only draw actors within the screen
            if r.right > self.draw_area[0] and r.left < self.draw_area[2]:
                if r.bottom > self.draw_area[1] and r.top < self.draw_area[3]:
                    surface.blit(actor_img, r)
                    
                    # Abilities
                    for ab in a.abilities:
                        if ab.image != None:
                            # First we want to get the image
                            ab_rounded_facing = screen_lib.get_facing_angle(ab.facing[0], self.engine.facings)
                            ab_img_name = "%s_%s_%s" % (
                                ab.image,
                                self.engine.images[ab.image].real_frame(a.frame),
                                ab_rounded_facing
                            )
                            
                            if ab_img_name not in self.image_cache:
                                self.image_cache[ab_img_name] = screen_lib.make_rotated_image(
                                    image = self.engine.images[ab.image].get(a.frame),
                                    angle = ab_rounded_facing
                                )
                            
                            # We now need to work out our relative coordinates
                            rel_pos = ab.get_offset_pos()
                            
                            # Now we actually draw it
                            centre_offset = self.engine.images[ab.image].get_rotated_offset(ab_rounded_facing)
                            ability_img = self.image_cache[ab_img_name]
                            r = pygame.Rect(ability_img.get_rect())
                            r.left = a.pos[0] + self.draw_offset[0] - r.width/2 + centre_offset[0] + rel_pos[0]
                            r.top = a.pos[1] + self.draw_offset[1] - r.height/2 + centre_offset[1] + rel_pos[1]
                            surface.blit(ability_img, r)
                    
                    # Selection box?
                    if a.selected:
                        """Removed selection boxes for now as I'm not sure how I want them to work
                        with rotated actors"""
                        # selection_r = pygame.transform.rotate(a.selection_rect(), -rounded_facing)
                        # pygame.draw.rect(surf, (255, 255, 255), selection_r, 1)
                        
                        surface.blit(*a.health_bar(self.draw_offset[0], self.draw_offset[1]))
                        
                    # Draw completion box anyway
                    if a.completion < 100:
                        surface.blit(*a.completion_bar(self.draw_offset[0], self.draw_offset[1]))
            
            # Pass effects from the actor to the battle screen
            # this means that if the actor dies the effect still lives on
            while len(a.effects) > 0:
                self.sim.effects.append(a.effects.pop())
            
            # Do same with bullets
            while len(a.bullets) > 0:
                self.sim.bullets.append(a.bullets.pop())
        
        # Bullets
        for b in self.sim.bullets:
            # --- Using code similar to Actors ---
            
            bullet_img = self.engine.images[b.image].get()
            r = pygame.Rect(bullet_img.get_rect())
            r.left = b.pos[0] + self.draw_offset[0] - b.width/2
            r.top = b.pos[1] + self.draw_offset[1] - b.height/2
            
            # Only draw bullets within the screen
            if r.right > self.draw_area[0] and r.left < self.draw_area[2]:
                if r.bottom > self.draw_area[1] and r.top < self.draw_area[3]:
                    if b.image == "":
                        # Bullet is dynamically drawn
                        b.draw(surf, self.draw_offset)
                    else:
                        # Bullet has an image
                        surface.blit(bullet_img, r)
                
        # Draw effects last
        for i, e in enumerate(self.sim.effects):
            r = pygame.Rect(e.rect)
            r.left = e.rect.left + self.draw_offset[0]
            r.top = e.rect.top + self.draw_offset[1]
            
            # Only draw effects within the screen
            if r.right > self.draw_area[0] and r.left < self.draw_area[2]:
                if r.bottom > self.draw_area[1] and r.top < self.draw_area[3]:
                    e.draw(surf, self.draw_offset)
        
        # Placement (such as placing a building)
        if self.place_image:
            img = self.engine.images[self.place_image]
            r = img.get_rect()
            surface.blit(img.get(), pygame.Rect(
                self.mouse[0] - r.width/2, self.mouse[1] - r.height/2,
                r.width, r.height,
            ))
        
        # Controls
        for i, c in self.controls.items():
            if c.visible:
                c.update()
                if c.blit_image:
                    surface.blit(*c.image())
                else:
                    c.draw(surface)
            
            # surface.blit(*p.image())
        
        # Dragrect
        print(self.scroll_x, self.scroll_y)
        # print(self.scrolled_mousedown_at, self.scrolled_mousedrag_at)
        if self.scrolled_mousedown_at != None and self.scrolled_mousedrag_at != None:
            drag_rect = [
                self.scrolled_mousedown_at[0], self.scrolled_mousedown_at[1],
                self.scrolled_mousedrag_at[0], self.scrolled_mousedrag_at[1],
            ]
            
            pygame.draw.rect(surface, (255, 255, 255), drag_rect, 1)
        
        pygame.display.flip()
    
    def _handle_keyup(self, event):
        if event.key in self.keys_down:
            del(self.keys_down[event.key])
        
        mods = pygame.key.get_mods()
        
        # Number key? Select or assign a control group
        if event.key in NUMBERS:
            if KMOD_CTRL & mods:
                self.assign_control_group(event.key)
            else:
                self.select_control_group(event.key)
            
            return
        
        # Are they altering the mouse mode?
        if event.key in self.hotkeys:
            if len(self.sim.selected_actors) > 0:
                if self.hotkeys[event.key] == "move":
                    self.mouse_mode = "move"
                    
                if self.hotkeys[event.key] == "stop":
                    for a in self.sim.selected_actors:
                        if a.team == self.player_team:
                            if KMOD_SHIFT & mods:
                                self.queue_order(a, "stop")
                            else:
                                self.add_order(a, "stop")
                    
                if self.hotkeys[event.key] == "attack":
                    self.mouse_mode = "attack"
                
                if self.hotkeys[event.key] == "hold":
                    self.mouse_mode = "hold"
                
                if self.hotkeys[event.key] == "patrol":
                    self.mouse_mode = "patrol"
                
                if self.hotkeys[event.key] == "build":
                    self.mouse_mode = "build"
                
        
        self.handle_keyup(event)
    
    def _handle_keyhold(self):
        if time.time() >= self._next_scroll:
            # Up/Down
            if self.scroll_up_key in self.keys_down:
                self.scroll_up()
            elif self.scroll_down_key in self.keys_down:
                self.scroll_down()
            
            # Right/Left
            if self.scroll_right_key in self.keys_down:
                self.scroll_right()
            elif self.scroll_left_key in self.keys_down:
                self.scroll_left()
            
            self._next_scroll = time.time() + self.scroll_delay
        
        if len(self.keys_down) > 0:
            self.handle_keyhold()
    
    def _handle_mouseup(self, event, drag=False):
        self.true_mousedown_at = None
        self.scrolled_mousedown_at = None
        
        # If it's been less than X seconds since the last click
        # then it is a double click
        if time.time() <= self._last_mouseup[1] + self._double_click_interval:
            return self._handle_doubleclick(self._last_mouseup[0], event)
        
        # Save this incase it's the first part of a double click
        self._last_mouseup = [event, time.time()]
        
        # Controls
        for i, c in self.controls.items():
            if c.accepts_mouseup:
                if c.contains(event.pos):
                    try:
                        c.handle_mouseup(event, **c.mouseup_kwargs)
                        self.mouse_mode = None
                    except Exception as e:
                        print("Func: %s" % c.handle_mouseup)
                        print("Event: %s" % event)
                        print("Kwargs: %s" % c.mouseup_kwargs)
                        raise
        
        # Is there a callback setup for a mouseup?
        if self.mouseup_callback:
            callback_func, kwargs = self.mouseup_callback, self.mouseup_callback_kwargs
            
            # Set these to nothing now in case we want to make a new callback
            # in the current callback
            self.mouseup_callback = None
            self.mouseup_callback_kwargs = {}
            
            return callback_func(event, drag, **kwargs)
        
        # Now the main event
        mods = pygame.key.get_mods()
        scrolled_mouse_pos = (
            event.pos[0] - self.scroll_x,
            event.pos[1] - self.scroll_y
        )
        
        # Left click
        if event.button == 1:
            if not drag:
                self._left_click(event)
        
        # Right click
        elif event.button == 3:
            self._right_click(event)
            if len(self.sim.selected_actors) == 0:
                return
            
            self._right_click(event)
            
        else:
            print("battle_screen.handle_mouseup: event.button = %s" % event.button)
        
        self.mouse_mode = None
    
    
    def _left_click(self, event):
        mods = pygame.key.get_mods()
        scrolled_mouse_pos = (
            event.pos[0] - self.scroll_x,
            event.pos[1] - self.scroll_y
        )
        
        # If there is a mouse mode (such as attack) then we will want to issue
        # an order
        if self.mouse_mode != None:
            
            # Have we selected an actor to target?
            actor_target = None
            for aid, a in self.sim.actors.items():
                if actor_lib.contains_point(a, real_mouse_pos):
                    actor_target = weakref.ref(a)()
                    break
            
            # Immidiate or Queued?
            if KMOD_SHIFT & mods:
                for a in self.sim.selected_actors:
                    if a.team == self.player_team:
                        self.queue_order(a, self.key_mod, pos=real_mouse_pos, target=actor_target)
            else:
                for a in self.sim.selected_actors:
                    if a.team == self.player_team:
                        self.add_order(a, self.key_mod, pos=real_mouse_pos, target=actor_target)
        
        # No mouse order, we're just looking to select an actor
        else:
            if not KMOD_SHIFT & mods:
                self.unselect_all_actors()
            
            for aid, a in self.sim.actors.items():
                if a.contains_point(scrolled_mouse_pos):
                    self.left_click_actor(a)
                    break
        
    def _right_click(self, event):
        mods = pygame.key.get_mods()
        scrolled_mouse_pos = (
            event.pos[0] - self.scroll_x,
            event.pos[1] - self.scroll_y
        )
        
        # Have we targeted an actor?
        actor_target = None
        for aid, a in self.sim.actors.items():
            if actor_lib.contains_point(a, real_mouse_pos):
                actor_target = weakref.ref(a)()
                break
        
        # No actor clicked, this means we're moving
        if not actor_target:
            for a in self.sim.selected_actors:
                if a.team == self.player_team:
                    if KMOD_SHIFT & mods:
                        self.queue_order(a, "move", pos=real_mouse_pos)
                    else:
                        self.add_order(a, "move", pos=real_mouse_pos)
                    
        # An actor was clicked, we could be moving, attacking etc
        else:
            if actor_target.team != self.sim.selected_actors[0].team:
                for a in self.sim.selected_actors:
                    if a.team == self.player_team:
                        if KMOD_SHIFT & mods:
                            self.queue_order(a, "attack", target=actor_target)
                        else:
                            self.add_order(a, "attack", target=actor_target)
            else:
                for a in self.sim.selected_actors:
                    if a.team == self.player_team:
                        if KMOD_SHIFT & mods:
                            self.queue_order(a, "aid", target=actor_target)
                        else:
                            self.add_order(a, "aid", target=actor_target)
    
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
        
        scrolled_first_click = (
            first_click.pos[0] - self.scroll_x,
            first_click.pos[1] - self.scroll_y
        )
        
        scrolled_second_click = (
            second_click.pos[0] - self.scroll_x,
            second_click.pos[1] - self.scroll_y
        )
        
        # Now check actors
        for aid, a in self.sim.actors.items():
            if a.contains_point(scrolled_first_click) and a.contains_point(scrolled_second_click):
                self.double_left_click_actor(a)
                break
        
        self.handle_doubleclick(first_click, second_click)
    
    def _handle_mousedragup(self, event):
        self.true_mousedrag_at = None
        self.scrolled_mousedrag_at = None
        
        if self.scrolled_mousedown_at == None:
            return self.handle_mousedragup(event, None)
        
        scrolled_mouse_pos = (
            event.pos[0] - self.scroll_x,
            event.pos[1] - self.scroll_y
        )
        
        drag_rect = (
            min(self.scrolled_mousedown_at[0], scrolled_mouse_pos[0]),
            min(self.scrolled_mousedown_at[1], scrolled_mouse_pos[1]),
            max(self.scrolled_mousedown_at[0], scrolled_mouse_pos[0]),
            max(self.scrolled_mousedown_at[1], scrolled_mouse_pos[1]),
        )
        
        contains_friendly = False
        short_list = []
        if event.button == 1:
            if not KMOD_SHIFT & mods:
                self.unselect_all_actors()
            
            # First see if there are friendlies there
            # if the selection contains friendlies then we
            # should only select the friendlies
            for aid, a in self.sim.actors.items():
                if actor_lib.is_inside(a, drag_rect):
                    if a.team == self.player_team:
                        contains_friendly = True
                    short_list.append(a)
            
            # Now to select them
            for a in short_list:
                if contains_friendly:
                    if a.team == self.player_team:
                        self.sim.select_actor(a)
                else:
                    self.sim.select_actor(a)
        
        self.handle_mousedragup(event, drag_rect)
    
    def scroll_right(self, rate = 1):
        self.scroll_x += rate * self.scroll_speed
        self.scroll_x = min(self.scroll_boundaries[2], self.scroll_x)
        
        self.draw_offset[0] = self.scroll_x + self.draw_area[0]
    
    def scroll_left(self, rate = 1):
        self.scroll_x -= rate * self.scroll_speed
        self.scroll_x = max(self.scroll_boundaries[0], self.scroll_x)
        
        self.draw_offset[0] = self.scroll_x + self.draw_area[0]
        
    def scroll_down(self, rate = 1):
        self.scroll_y += rate * self.scroll_speed
        self.scroll_y = min(self.scroll_boundaries[3], self.scroll_y)
        
        self.draw_offset[1] = self.scroll_y + self.draw_area[1]
        
    def scroll_up(self, rate = 1):
        self.scroll_y -= rate * self.scroll_speed
        self.scroll_y = max(self.scroll_boundaries[1], self.scroll_y)
        
        self.draw_offset[1] = self.scroll_y + self.draw_area[1]
    
    def scroll_to_coords(self, x, y):
        """Scroll so that the coords x,y are at the centre of the view"""
        
        self.scroll_x = - x + self.engine.window_width/2
        self.scroll_y = - y + self.engine.window_height/2
        
        # Boundaries
        self.scroll_x = min(self.scroll_boundaries[2], max(self.scroll_boundaries[0], self.scroll_x))
        self.scroll_y = min(self.scroll_boundaries[3], max(self.scroll_boundaries[1], self.scroll_y))
        
        # Alter draw margin
        self.draw_offset[0] = self.scroll_x + self.draw_area[0]
        self.draw_offset[1] = self.scroll_y + self.draw_area[1]
    
    def left_click_actor(self, act):
        """Invert selection on actor"""
        if act.selected:
            self.unselect_actor(act)
        else:
            self.select_actor(act)
    
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
    
    # def place_actor_mode(self, actor_type):
    #     """Used to enter placement mode where an icon hovers beneath the
    #     cursor and when clicked is built or suchlike"""
    #     
    #     self.place_image = self.actor_types[actor_type]['placement_image']
    #     
    #     self.mouseup_callback = self.place_actor_from_click
    #     self.mouseup_callback_args = [{"type":actor_type}]
    
    def selection_changed(self):
        """docstring for selection_changes"""
        pass

    
