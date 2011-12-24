import unittest
from sequtus.libs import vectors

class VectorTests(unittest.TestCase):
    def test_init(self):
        vals = (
            ([0,1,2],   [0,1,2]),
            (1,         [1,0,0]),
            ([0,1],     [0,1,0]),
            
            ([-5,-4,-6],[-5,-4,-6]),
        )
        
        for args, expected in vals:
            if type(args) == list:
                self.assertEqual(vectors.V(*args).v, expected)
            self.assertEqual(vectors.V(args).v, expected)
    
    def test_equals(self):
        vals = (
            ([1,2,3],   [1,2,3],    True),
            ([-1,-2,-3],[-1,-2,-3], True),
            
            ([1,2,3],   [0,2,3],    False),
            ([1,2,3],   [1,0,3],    False),
            ([1,2,3],   [1,2,0],    False),
            
            ([1,1,1],   [2,2,2],    False),
        )
        
        for v1, v2, expected in vals:
            if expected:
                self.assertEqual(vectors.V(v1), vectors.V(v2))
            else:
                self.assertNotEqual(vectors.V(v1), vectors.V(v2))
    
    def test_operators(self):
        # Addition
        add_vals = (
            ([0,0,0], [1,1,1], [1,1,1]),
            ([2,2,2], [1,1,1], [3,3,3]),
            ([0,0,0], [0,0,0], [0,0,0]),
            ([3,5,7], [0,5,0], [3,10,7]),
        )
    
        for v1, v2, expected in add_vals:
            self.assertEqual(vectors.V(v1) + vectors.V(v2), expected)
            self.assertEqual(vectors.V(v1) + v2, expected)
        
        # Subtraction
        subtract_vals = (
            ([0,0,0], [1,1,1], [-1,-1,-1]),
            ([2,2,2], [1,1,1], [1,1,1]),
            ([0,0,0], [0,0,0], [0,0,0]),
            ([3,5,7], [0,5,0], [3,0,7]),
        )
        
        for v1, v2, expected in subtract_vals:
            self.assertEqual(vectors.V(v1) - vectors.V(v2), expected)
            self.assertEqual(vectors.V(v1) - v2, expected)
        
        # Multiplication
        multiply_vals = (
            ([0,0,0], [1,1,1], [0,0,0]),
            ([2,2,2], [1,2,1], [2,4,2]),
            ([0,0,0], [0,0,0], [0,0,0]),
            ([3,5,7], [2,5,0], [6,25,0]),
        )
        
        for v1, v2, expected in multiply_vals:
            self.assertEqual(vectors.V(v1) * vectors.V(v2), expected)
            self.assertEqual(vectors.V(v1) * v2, expected)
        
        # Division
        divide_vals = (
            ([0,0,0], [1,2,1], [0,0,0]),
            ([2,2,2], [1,2,1], [2,1,2]),
            ([0,0,0], [1,1,1], [0,0,0]),
            ([3,5,7], [2,2,1], [1.5,2.5,7]),
        )
        
        for v1, v2, expected in divide_vals:
            self.assertEqual(vectors.V(v1) / vectors.V(v2), expected)
            self.assertEqual(vectors.V(v1) / v2, expected)
        
        # Absolute
        abs_vals = (
            ([-1,0,0], [1,0,0]),
            ([2,-2,2], [2,2,2]),
            ([0,-1,0], [0,1,0]),
            ([3,5,-7], [3,5,7]),
        )
        
        for v1, expected in abs_vals:
            self.assertEqual(abs(vectors.V(v1)), expected)
    
    def test_magnitude(self):
        vals = (
            ([3,4,0], 5),
            ([4,4,4], 6.928),
        )
        
        for v1, expected in vals:
            self.assertAlmostEqual(vectors.V(v1).magnitude(), expected, places=2)
    
    def test_bound_angle(self):
        vals = (
            # 2D
            (360, 0),
            (0, 0),
            (-360, 0),
            (359, 359),
            (360 + 359, 359),
            
            # 3D
            ([50, 50], [50, 50]),
            ([360, 0], [0, 0]),
            ([-360, 360], [0, 0]),
        )
        
        for a, expected in vals:
            self.assertEqual(expected, vectors.bound_angle(a))
    
    def test_move_to_vector(self):
        vals = (
            ((0,0), 10, (0,-10,0)),# Up
            ((90,0), 10, (10,0,0)),# Right
            ((180,0), 10, (0,10,0)),# Down
            ((270,0), 10, (-10,0,0)),# Left
            
            ((45,0), 10, (7.07, -7.07, 0)),# Up - right
            ((135,0), 10, (7.07, 7.07, 0)),# Down - right
            ((225,0), 10, (-7.07, 7.07, 0)),# Down - left
            ((315,0), 10, (-7.07, -7.07, 0)),# Up - left
            
            # Now all the above with a 45 degree upward tilt too
            # ([0,45], 10, [0,-10,-7.07]),# Up
            # ([90,45], 10, [10,0,0]),# Right
            # ([180,45], 10, [0,10,0]),# Down
            # ([270,0], 10, [-10,0,0]),# Left
            # 
            # ([45,45], 10, [7.07, -7.07, 0]),# Up - right
            # ([135,45], 10, [7.07, 7.07, 0]),# Down - right
            # ([225,45], 10, [-7.07, 7.07, 0]),# Down - left
            # ([315,45], 10, [-7.07, -7.07, 0]),# Up - left
        )
        
        for angle, distance, expected in vals:
            answer = vectors.move_to_vector(angle, distance)
            
            try:
                self.assertAlmostEqual(answer[0], expected[0], places=2)
                self.assertAlmostEqual(answer[1], expected[1], places=2)
                self.assertAlmostEqual(answer[2], expected[2], places=2)
            except Exception as e:
                print("\n\nAngle: %s, Distance: %s, Expected: %s, Got: %s" % (angle, distance, expected, answer))
                raise
    
    def test_distance(self):
        vals = (
            # 3D
            ([0,0,0], 0),
            ([1,1,1], 1.73),
            ([3,4,0], 5),
            ([3,0,4], 5),
        )
        
        for the_point, expected in vals:
            self.assertAlmostEqual(vectors.distance(the_point), expected, places=2)
    
    def test_angle_diff(self):
        vals = (
            (10, 100, 90),# Right
            (100, 10, -90),# Left
            
            # Cross the 360 mark
            (350, 10, 20),
            (10, 350, -20),
            
            # Now in 3D
            ([10, 20], [100, 0], [90, -20]),
            ([100, 0], [10, 30], [-90, 30]),
            ([350, 10], [10, 65], [20, 55]),
            ([10, 40], [350, 0], [-20, -40]),
        )
        
        for a1, a2, expected in vals:
            self.assertEqual(vectors.angle_diff(a1, a2), expected)
    
    def test_angle(self):
        # First we test the function with an argument
        vals = (
            # XY Tests
            ([0,0,0], [4,-4,0], [45, 0]),# Up and right
            ([0,0,0], [4,4,0], [135, 0]),# Down and right
            ([0,0,0], [-4,4,0], [225, 0]),# Down and left
            ([0,0,0], [-4,-4,0], [315, 0]),# Up and left
            
            # Same as before but scaled up in size
            ([0,0,0], [400,-400,0], [45, 0]),# Up and right
            ([0,0,0], [1000,1000,0], [135, 0]),# Down and right
            ([0,0,0], [-0.5,0.5,0], [225, 0]),# Down and left
            ([0,0,0], [-50000,-50000,0], [315, 0]),# Up and left
            
            ([0,0,0], [0,-4,0], [0, 0]),# Dead Up
            ([0,0,0], [4,0,0], [90, 0]),# Dead Right
            ([0,0,0], [0,4,0], [180, 0]),# Dead Down
            ([0,0,0], [-4,0,0], [270, 0]),# Dead Left
            
            # Specific XY tests
            ([1,1,0], [4,100,0], [178.26, 0]),# Down and a little bit right
            ([400, 400, 0], [100, 900, 0], [210.963,0]),# Down and left
            
            # Z Tests
            # ([0,0,0], [4,-4,0], [0, 45]),# Aim up
            # ([0,0,0], [4,4,0], [135, 0]),# Aim down
            # ([0,0,0], [-4,4,0], [225, 0]), 
            # ([0,0,0], [-4,-4,0], [315, 0]),
        )
        
        for v1, v2, expected in vals:
            r1, r2 = vectors.V(v1).angle(v2)
            
            self.assertAlmostEqual(r1, expected[0], places=2, msg="vectors.angle(%s, %s) should equal %s, instead got %s" % (
                v1, v2, expected[0], r1
            ))
            self.assertAlmostEqual(r2, expected[1], places=2)
    
        
        # Now we test the function with no argument
        vals = (
            # XY Tests
            ([4,-4,0], [45, 0]),# Up and right
            ([4,4,0], [135, 0]),# Down and right
            ([-4,4,0], [225, 0]),# Down and left
            ([-4,-4,0], [315, 0]),# Up and left
            
            # Same as before but scaled up in size
            ([400,-400,0], [45, 0]),# Up and right
            ([1000,1000,0], [135, 0]),# Down and right
            ([-0.5,0.5,0], [225, 0]),# Down and left
            ([-50000,-50000,0], [315, 0]),# Up and left
            
            ([0,-4,0], [0, 0]),# Dead Up
            ([4,0,0], [90, 0]),# Dead Right
            ([0,4,0], [180, 0]),# Dead Down
            ([-4,0,0], [270, 0]),# Dead Left
        )
        
        for a, expected in vals:
            r, r2 = vectors.V(a).angle()
            self.assertAlmostEqual(r, expected[0], places=2, msg="vectors.angle(%s) should equal %s, instead got %s" % (
                a, expected[0], r
            ))
            self.assertAlmostEqual(r2, expected[1], places=2)
    
    def test_midpoint(self):
        vals = (
            ([10,10,0], [15,5,0], 1, [10.707, 9.292, 0]),
            ([10,10,0], [15,5,0], 5, [13.535, 6.464, 0]),
            
            ([0,0,0], [100,100,0], 20, [14.14, 14.14, 0]),
            
            # Now 3D
            ([10,10,10], [15,5,0], 5, [13.535, 6.464, 14.082]),
        )
        
        for pos1, pos2, distance, expected in vals:
            x,y,z = vectors.get_midpoint(pos1, pos2, distance)
            
            try:
                self.assertAlmostEqual(expected[0], x, places=2)
                self.assertAlmostEqual(expected[1], y, places=2)
                self.assertAlmostEqual(expected[2], z, places=2)
            except Exception as e:
                print("\n\nTrying to midpoint({}, {}, {})\n\n".format(pos1, pos2, distance))
                raise
    


suite = unittest.TestLoader().loadTestsFromTestCase(VectorTests)
