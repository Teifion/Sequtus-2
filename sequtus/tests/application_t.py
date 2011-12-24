import unittest
import traceback
import sys

from sequtus.game import application_core
from sequtus.defaults import core

class TestCore (core.DefaultCore):
    """Identical to a normal core except it doesn't loop a load of times"""
    def __enter__(self):
        try:
            self.startup()
            self.set_screen("battle")
            self.loop()
        
        except Exception as e:
            # traceback.print_exc(file=sys.stdout)
            
            if self.current_screen != None:
                self.current_screen.quit()
            
            raise
        
        return self
    
    def __exit__(self, exc_type, exc_value, traceback):
        pass
    
    # Override this as it uses a loop
    def start(self, screen):
        pass
    
    def loop(self):
        try:
            # Update and redraw calls
            self.current_screen._update()
            self.current_screen._redraw()
        except Exception as e:
            # traceback.print_exc(file=sys.stdout)
            
            if self.current_screen != None:
                self.current_screen.quit()
            
            raise


class ApplicationTests(unittest.TestCase):
    pass
        
suite = unittest.TestLoader().loadTestsFromTestCase(ApplicationTests)
