from __future__ import division
import math

class V (object):
    """An object designed to allow vector math to be performed
    A vector can represent a position or a velocity"""
    def __init__(self, x, y=0, z=0):
        super(V, self).__init__()
        if type(x) == list or type(x) == tuple:
            # It tries to get the 3rd item but can handle a 2D input
            self.v = [x[0], x[1], x[2] if len(x) > 2 else 0]
        else:
            self.v = [x,y,z]
    
    # Emulation of a sequence
    def __getitem__(self, key):
        if type(key) == int:
            return self.v[key]
        else:
            raise IndexError("No key of %s" % key)
    
    # Using this we are able to ask if a Vector equals a list or tuple
    def __eq__(self, other):
        if type(other) == list or type(other) == tuple:
            other = V(other)
        return self.v == other.v
    
    # At heart this is designed to be a mathematical object
    def __add__(self, other):
        if type(other) != V: other = V(other)
        return V([self.v[i] + other.v[i] for i in range(3)])
    
    def __sub__(self, other):
        if type(other) != V: other = V(other)
        return V([self.v[i] - other.v[i] for i in range(3)])
        
    def __mul__(self, other):
        if type(other) != V: other = V(other)
        return V([self.v[i] * other.v[i] for i in range(3)])
    
    def __div__(self, other):
        if type(other) != V: other = V(other)
        return V([self.v[i] / other.v[i] for i in range(3)])
    
    # More math functions
    def __abs__(self):
        return V([abs(self.v[i]) for i in range(3)])
    
    def angle(self, v2=None):
        # If no second vector is passed we just want the angle of our
        # velocity, not the angle from 
        if v2 == None:
            v2 = self.v[:]
            v1 = [0,0,0]
        else:
            v1 = self.v[:]
        
        # SOH CAH TOA
        # We have the opposite and adjacent
        x = abs(v1[0] - v2[0])
        y = abs(v1[1] - v2[1])
        z = abs(v1[2] - v2[2])

        # Exacts, because in these cases we get a divide by 0 error
        if x == 0:
            if v1[1] >= v2[1]:# Up
                xy = 0
            elif v1[1] < v2[1]:# Down
                xy = 180
        elif y == 0:
            if v1[0] <= v2[0]:# Right
                xy = 90
            elif v1[0] > v2[0]:# Left
                xy = 270
        else:
            # Using trig
            if v1[1] > v2[1]:# Up
                if v1[0] < v2[0]:# Right
                    xy = math.degrees(math.atan(x/y))
                else:# Left
                    xy = math.degrees(math.atan(y/x)) + 270
            else:# Down
                if v1[0] < v2[0]:# Right
                    xy = math.degrees(math.atan(y/x)) + 90
                else:# Left
                    xy = math.degrees(math.atan(x/y)) + 180
        
        # UP DOWN
        hyp = math.sqrt(x*x + y*y)
        if hyp > 0:
            za = math.atan(z/hyp)
        else:
            za = 0
        
        return [xy, math.degrees(za)]
    
    def magnitude(self):
        x,y,z = self.v
        
        a = math.sqrt(x**2 + y**2)
        return math.sqrt(a*a + z*z)    
    
    def as_move(self):
        return [self.angle(), self.magnitude()]
    
    def distance(self, the_point=None):
        """If pos2 is left out then it gives distance to pos1 from origin"""
        if the_point == None:
            the_point = [0 for i in range(3)]
        
        if type(the_point) != V:
            the_point = V(the_point)
        
        x = abs(self.v[0] - the_point.v[0])
        y = abs(self.v[1] - the_point.v[1])
        z = abs(self.v[2] - the_point.v[2])
        a = math.sqrt(x*x + y*y)
        
        return math.sqrt(a*a + z*z)

def distance(the_point):
    """Returns the distance from the origin to the point. It's really just
    a wrapper around V.distance."""
    return V(the_point).distance()

def bound_angle(angle):
    """Returns an angle between the values of 0 and 360, preventing you
    ending up with angles like -100 or 420"""
    if type(angle) == list or type(angle) == tuple:
        return [bound_angle(angle[0]), bound_angle(angle[1])]
    
    while angle >= 360: angle -= 360
    while angle < 0: angle += 360
    return angle

def angle_diff(angle1, angle2=0):
    """Gives the amount you need to turn by to get from angle1 to angle2
    
    will provide a minus number if you turn counter-clockwise"""
    
    if type(angle1) == list or type(angle1) == tuple:
        return [angle_diff(angle1[0], angle2[0]), angle_diff(angle1[1], angle2[1])]
    
    # Distance going right
    if angle1 > angle2:# We cross 360
        right = angle2 - angle1 + 360
    else:
        right = angle2 - angle1
    
    # Distance going left
    if angle2 > angle1:# We cross 360
        left = angle1 - angle2 + 360
    else:
        left = angle1 - angle2
    
    # Now return the shortest path
    if abs(right) < abs(left):
        return right
    else:
        return -left

def move_to_vector(angle, distance):
    """
    Takes an angle (length 2 sequence) and a distance, returns a Vector
    """
    angle = bound_angle(angle)
    
    # First we get the vertical plane
    z, h = _move_to_vector_2d(angle[1], distance)
    
    # Hypotenuse cannot be negative in length
    h = abs(h)
    
    # Now horrizontal
    x, y = _move_to_vector_2d(angle[0], h)
    
    return V(x, y, z)

def _move_to_vector_2d(angle, distance):
    """Returns an opposite and adjacent from the triangle"""
    
    if angle == 0:      return 0, -distance
    if angle == 90:     return distance, 0
    if angle == 180:    return 0, distance
    if angle == 270:    return -distance, 0
    
    opp = math.sin(math.radians(angle)) * distance
    adj = math.cos(math.radians(angle)) * distance
    
    return [opp, -adj]

def get_midpoint(pos1, pos2, distance):
    """
    Given pos1 and pos2 it determines where pos1 will end up if it travels "distance" towards pos2.
    """
    a, za = V(pos1).angle(pos2)
    
    x = pos1[0] + (math.sin(math.radians(a)) * distance)
    y = pos1[1] - (math.cos(math.radians(a)) * distance)
    z = pos1[2] + (math.sin(math.radians(za)) * distance)
    
    return [x,y,z]
    
