import pygame
import unittest

from sequtus.game import actors
from sequtus.tests import application_t


class BattleSimTests(unittest.TestCase):
    def test_place_actor(self):
        with application_t.TestCore() as c:
            sim = c.current_screen.sim
            
            self.assertEqual(1, len(sim.actors))
            oid = sim.place_actor({"type":"Worker", "team":1}).oid
            self.assertEqual(2, len(sim.actors))
            
            self.assertIn(oid, sim.actors)
    
    def test_add_orders(self):
        with application_t.TestCore() as c:
            sim = c.current_screen.sim
            
            a = sim.actors[0]
            
            # First test adding it with an int actor and int target
            sim.orders_to_send = []
            sim.add_order(the_actor=a.oid, command="move", pos=[100,100], target=0)
            self.assertEqual(sim.orders_to_send, [(0, "move", [100,100], 0)])
            
            # Ref actor, int target
            sim.orders_to_send = []
            sim.add_order(the_actor=a, command="move", pos=[100,100], target=0)
            self.assertEqual(sim.orders_to_send, [(0, "move", [100,100], 0)])
            
            # Int actor, ref target
            sim.orders_to_send = []
            sim.add_order(the_actor=a.oid, command="move", pos=[100,100], target=a)
            self.assertEqual(sim.orders_to_send, [(0, "move", [100,100], 0)])
            
            # Ref actor, Ref target
            sim.orders_to_send = []
            sim.add_order(the_actor=a, command="move", pos=[100,100], target=a)
            self.assertEqual(sim.orders_to_send, [(0, "move", [100,100], 0)])
        
    def test_queue_orders(self):
        with application_t.TestCore() as c:
            sim = c.current_screen.sim
            
            a = sim.actors[0]
            
            # First test adding it with an int actor and int target
            sim.orders_to_queue = []
            sim.queue_order(the_actor=a.oid, command="move", pos=[100,100], target=0)
            self.assertEqual(sim.orders_to_queue, [(0, "move", [100,100], 0)])
            
            # Ref actor, int target
            sim.orders_to_queue = []
            sim.queue_order(the_actor=a, command="move", pos=[100,100], target=0)
            self.assertEqual(sim.orders_to_queue, [(0, "move", [100,100], 0)])
            
            # Int actor, ref target
            sim.orders_to_queue = []
            sim.queue_order(the_actor=a.oid, command="move", pos=[100,100], target=a)
            self.assertEqual(sim.orders_to_queue, [(0, "move", [100,100], 0)])
            
            # Ref actor, Ref target
            sim.orders_to_queue = []
            sim.queue_order(the_actor=a, command="move", pos=[100,100], target=a)
            self.assertEqual(sim.orders_to_queue, [(0, "move", [100,100], 0)])
            
            
            
            
            
            


suite = unittest.TestLoader().loadTestsFromTestCase(BattleSimTests)
