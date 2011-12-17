"""
This code is released as-is with no warranty of any sort.

You are welcome to alter and distribute though I'd
appreciate credit being given where possible.

Written by Teifion Jordan (http://woarl.com)

Usage: covers.get_coverage()

suite is expected to be a unittest.TestSuite
root_dir is the root directory to start scanning from

module_skip and dirs_skip are a list of strings of the relevant modules and
    dirs to miss from the scan (3rd party libraries for example)

output_mode is the mode in which the results are output

In each unittest.TestCase instance you need to add a property of
"test_targets" as a list of functions and classes that test case
targets so that covers knows what is covered.
"""

import os
import re
import sys
import unittest
import webbrowser
from collections import OrderedDict

get_module_name = re.compile(r'.*?/?(.*?)\.py')

def get_coverage(suite, root_dir="default", verbose = True, module_skip = [], dirs_skip = [], output_mode="print"):
    if root_dir == "default":
        root_dir = "%s/" % sys.path[0]
    
    modules = OrderedDict()
    module_skip.extend(["__init__", "covers"])
    dirs_skip.extend(["__pycache__", ".git"])
    
    output = []
    
    # First we need a list of all the modules we want to look at, we simply walk through all folders in the root directory
    for root, dirs, files in os.walk(root_dir):
        for d in dirs_skip:
            if d in dirs: dirs.remove(d)
        
        folder = root.replace(root_dir, "")
        
        for f in files:
            # We only want to look at python files
            if "".join(f[-3:len(f)]) == '.py':
                file_name = get_module_name.search(f)
                if file_name != None:
                    file_name = file_name.groups()[0].strip()
                else:
                    raise Warning("The file {0} passed the .py test but no match was found".format(f))
                
                if file_name in module_skip:
                    continue
                
                # Now to actually import it
                if folder == "":
                    try:
                        coverage_module = __import__(file_name)
                    except ImportError as e:
                        print("Error importing {0}".format(file_name))
                        raise
                else:
                    try:
                        coverage_module = __import__(folder.replace("/", "."), fromlist=[file_name])
                        coverage_module = getattr(coverage_module, file_name)
                    except ValueError as e:
                        print("Error importing {0}.{1}".format(folder.replace("/", "."), file_name))
                        print("Folder: {0}, File: {1}".format(folder, file_name))
                        raise
                    except ImportError as e:
                        print("Error importing {0}.{1}".format(folder.replace("/", "."), file_name))
                        print("Folder: {0}, File: {1}".format(folder, file_name))
                        raise
                
                # Now we add it to our list
                modules[(folder, file_name)] = coverage_module
    
    # Examine the test result data
    test_program_info = get_test_targets(suite)
    # test_program_info = get_test_targets(test_program.test)
    
    # Stats
    covered = 0
    total = 0
    red, yellow, green = 0, 0, 0
    
    # Run through each module to get all classes and functions
    last_folder = ''
    output.append("/")
    for path, the_module in modules.items():
        
        folder, module_name = path
        
        # We need to print the folder we're looking into
        if last_folder != folder:
            last_folder = folder
            output.append("\n{0}".format(folder))
        
        # Look at this module and work out what we've covered in it
        line, temp_covered, temp_total = evaluate_module(module_name, the_module, test_program_info, verbose)
        
        if line:
            output.append(line)
        
        # Stats stuff
        covered += temp_covered
        total += temp_total
        
        if temp_total == 0: continue
        if temp_covered < temp_total:
            if temp_covered > 0:
                yellow += 1
            else:
                red += 1
        else:
            green += 1
    
    
    if total != 0:
        percentage = (covered/total)*100
    else:
        percentage = 0
    
    # Now print out final verdict
    if output_mode == "web":
        output_html(output, covered, total, green, yellow, red)
    
    elif output_mode == "print":
        print("\n".join([colour_text(s) for s in output]))
        print("")
        print("%d out of %d (%d%%)" % (covered, total, percentage))
        print("%d greens" % green)
        print("%d yellows" % yellow)
        print("%d reds" % red)
    
    elif output_mode == "summary":
        print("%d out of %d (%d%%)" % (covered, total, (percentage)))
        print("%d greens" % green)
        print("%d yellows" % yellow)
        print("%d reds" % red)

def output_html(output, covered, total, green, yellow, red):
    html = []
    
    html_patterns = (
        (re.compile(r"''([^']*)''"),        r"<strong>\1</strong>"),
        (re.compile(r'__([^_]*)__'),        r'<em>\1</em>'),
        (re.compile(r"\*\*([^*]*)\*\*"),    r"<blink>\1</blink>"),

        (re.compile(r"\[r\](.*?)\[\/r\]"),  r"<span style='color: #A00;'>\1</span>"),
        (re.compile(r"\[g\](.*?)\[\/g\]"),  r"<span style='color: #0A0;'>\1</span>"),
        (re.compile(r"\[y\](.*?)\[\/y\]"),  r"<span style='color: #AA0;'>\1</span>"),
        (re.compile(r"\[b\](.*?)\[\/b\]"),  r"<span style='color: #00A;'>\1</span>"),
        (re.compile(r"\[m\](.*?)\[\/m\]"),  r"<span style='color: #A0A;'>\1</span>"),
        (re.compile(r"\[c\](.*?)\[\/c\]"),  r"<span style='color: #0AA;'>\1</span>"),
    )
    
    for l in output:
        text = l
        for regex, replacement in html_patterns:
            text = regex.sub(replacement, text)
        
        html.append(text)
    
    
    with open('/tmp/covers_py.html', 'w') as f:
        f.write("<pre>")
        f.write("\n".join(html))
        f.write("</pre>")
    
    webbrowser.open('file:///tmp/covers_py.html')

def get_test_targets(suite):
    targets = set()
    
    for module_tests in suite._tests:
        for t in module_tests._tests:
            try:
                for f in t.test_targets:
                    targets.add(f)
            except AttributeError as e:
                # It's assumed it has no targets
                pass
    
    return list(targets)

skipables = ("<type 'int'>", "<type 'str'>", "<type 'module'>",
    "<type 'NoneType'>", "<type 'dict'>", "<type 'tuple'>", "<type 'list'>"
)

SRE_Pattern = type(re.compile(""))
def get_testables(the_module):
    functions, classes = [], []
    for d in dir(the_module):
        f = getattr(the_module, d)
        
        # These cause errors and we don't want to match them anyway
        if type(f) == SRE_Pattern: continue
        
        # If it's a function we add it to the list
        # In Python 3 we use <class not <type
        if str(f.__class__) == "<type 'function'>":
            if f.__module__ == the_module.__name__:
                functions.append(f)
        elif str(f.__class__) == "<type 'type'>":
            # If it's a class and from this module then want both it and any functions it may have
            if f.__module__ == the_module.__name__ or True:
                classes.append((f, get_type_functions(the_module, f)))
        elif str(f.__class__) in skipables:
            continue
        else:
            pass
            # print(f.__class__, str(f)[0:20])
    
    return functions, classes

def get_type_functions(the_module, the_type):
    functions = []
    
    for d in dir(the_type):
        f = getattr(the_type, d)
        
        if str(f.__class__) == "<class 'function'>" or str(f.__class__) == "<type 'instancemethod'>":
            if f.__name__ != '__init__':
                if f.__module__ == the_module.__name__:
                    functions.append(f)
    
    return functions

def evaluate_module(module_name, the_module, test_program_info, verbose=False):
    output = []
    functions, classes = get_testables(the_module)
    function_count = len(functions)
    
    # Each function/class that is a part of the module
    covered_functions = 0
    for f in functions:
        function_count += 1
        
        if f in test_program_info:
            covered_functions += 1
            output.append("    [g]%s[/g]" % f.__name__)
        else:
            output.append("    [r]%s[/r]" % f.__name__)
    
    # Now classes
    for c, funcs in classes:
        function_count += len(funcs)
        
        if len(funcs) == 0:
            continue
        
        if sum([1 if f not in test_program_info else 0 for f in funcs]) > 0:
            all_tested = False
        else:
            all_tested = True
        
        # Class data
        if all_tested:
            output.append("    [g]%s[/g]" % c.__name__)
        else:
            output.append("    [r]%s[/r]" % c.__name__)
        
        for f in funcs:
            if f in test_program_info:
                covered_functions += 1
                output.append("      [g]%s[/g]" % f.__name__)
            else:
                output.append("      [r]%s[/r]" % f.__name__)
    
    # If there were no functions we can call it quits now
    if function_count == 0:
        if verbose:
            return "  %s has no functions" % module_name, 0, 0
        else:
            return None, 0, 0
    
    # At the top of the pile is the module name and it's stats
    if covered_functions < function_count:
        if covered_functions > 0:
            h = "  [y]{0:24}[/y] ({1}/{2}, {3}%)".format(module_name, covered_functions, function_count, round((covered_functions/function_count)*100))
        else:
            h = "  [r]{0:24}[/r] ({1}/{2}, 0%)".format(module_name, covered_functions, function_count)
    else:
        h = "  [g]{0:24}[/g] ({1}/{2}, 100%)".format(module_name, covered_functions, function_count)
    
    # And now we bundle it all up
    if verbose:
        output.insert(0, h)
        return "\n".join(output), covered_functions, function_count
    else:
        return h, covered_functions, function_count
    
    

shell_patterns = (
    (re.compile(r"''([^']*)''"),        '\033[1;1m\\1\033[30;0m'),
    (re.compile(r'__([^_]*)__'),        '\033[1;4m\\1\033[30;0m'),
    (re.compile(r"\*\*([^*]*)\*\*"),    '\033[1;5m\\1\033[30;0m'),
    
    (re.compile(r"\[r\](.*?)\[\/r\]"),  '\033[31m\\1\033[30;0m'),
    (re.compile(r"\[g\](.*?)\[\/g\]"),  '\033[32m\\1\033[30;0m'),
    (re.compile(r"\[y\](.*?)\[\/y\]"),  '\033[33m\\1\033[30;0m'),
    (re.compile(r"\[b\](.*?)\[\/b\]"),  '\033[34m\\1\033[30;0m'),
    (re.compile(r"\[m\](.*?)\[\/m\]"),  '\033[35m\\1\033[30;0m'),
    (re.compile(r"\[c\](.*?)\[\/c\]"),  '\033[36m\\1\033[30;0m'),
)

def colour_text(text):
    """
    Converts text to display in the shell with pretty colours
    
    Bold:           ''{TEXT}''
    Underline:      __{TEXT}__
    Blink:          **{TEXT}**
    
    Colour:         [colour]{TEXT}[/colour]
    Colours supported: Red, Green, Yellow, Blue, Magenta, Cyan
    """
    if type(text) != str:
        return text
    
    for regex, replacement in shell_patterns:
        text = regex.sub(replacement, text)
    
    return text
