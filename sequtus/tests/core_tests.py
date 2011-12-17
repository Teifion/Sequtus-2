import sys
import unittest

import covers
from sequtus.tests import *

def run(args):
    # Tests that don't take long to run
    fast_tests = [
        ai_lib_t.suite,
        actor_t.suite,
        vector_t.suite,
        geometry_t.suite,
        # battle_t.suite,
        screen_lib_t.suite,
        object_base_t.suite,
        
        # Screens
        battle_io_t.suite,
        battle_screen_t.suite,
        battle_sim_t.suite,
    ]
    
    # Tests that take a while to run
    slow_tests = [
        screen_t.suite,
    ]
    
    if args.all:
        suite = unittest.TestSuite(fast_tests + slow_tests)
    else:
        suite = unittest.TestSuite(fast_tests)
    
    
    if args.verbose == True:
        verbosity = 2
    else:
        verbosity = 1
    
    test_result = unittest.TextTestRunner(verbosity=verbosity).run(suite)
    
    # Covers currently doesn't work correctly
    return
    if test_result.failures == [] and test_result.errors == []:
        module_skip = ["main"]
        dirs_skip = ['test_lib', 'media', 'screenshots']
        
        if True or args.v:
            output_mode = "print"
        else:
            output_mode = "summary"
        
        covers.get_coverage(suite,
            verbose=args.verbose,
            module_skip = module_skip,
            dirs_skip = dirs_skip,
            output_mode=output_mode)
