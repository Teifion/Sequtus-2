import sys
import argparse

import sequtus

def default():
    from sequtus.defaults import core
    g = core.DefaultCore()
    g.start("battle")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Sequtus command line interface.', prog="sequtus")
    parser.add_argument('mode', default="run", help='the mode being run with, list modes with mode set to "list"')
    parser.add_argument('-v', dest="verbose", action="store_true", help='Verbose mode')
    parser.add_argument('-a', dest="all", action="store_true", help='all mode means everything is run', required=False)
    
    # If no args then default mode
    if len(sys.argv) > 1:
        args = parser.parse_args()
    else:
        default()
        exit()
    
    # Test modes
    if args.mode == 'test':
        from sequtus.tests import core_tests
        
        core_tests.run(args)
    
    # Profile code for optimisation
    elif args.mode == 'profile':
        from profile_lib import profiler
        profiler.run(args)
    
    # View profile results
    elif args.mode == 'view':
        from profile_lib import profiler
        profiler.view(args)
    
    # Run default function
    else:
        default()


