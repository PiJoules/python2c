#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import print_function

import re
import sys

from blocks import Block, StringBlock, FunctionBlock


def includes(code):
    """
    Return a list of #includes that are necessary to run the
    C code.
    """
    includes = []
    if any("print" in line for line in code):
        includes.append(StringBlock("#include <stdio.h>"))

    # Add a blank line for no reason
    includes.append(StringBlock())

    return includes


def main_func():
    """
    Return a standard main function block.
    """
    main_block = FunctionBlock("int", "main")
    return main_block


def should_ignore_line(line):
    """
    Determine whether or not a line should be ignored for now.
    """
    patterns_to_ingore = [
        re.compile('#!/usr/bin/env python'),
        re.compile('from __future__ import .+')
    ]
    return any(p.search(line) for p in patterns_to_ingore)


def should_keep_line(line):
    """
    Just the oposite of should_ignore_line.
    Wanted to use should_ignore_line in a filter function, but
    coudln't do 'code = filter(not should_ignore_line, code)'
    """
    return not should_ignore_line(line)


def parse_print(line):
    """
    Simple translation of a static string.
    """
    return re.sub(r"print\(\"([^\"]*)\"\)", r'printf("\1\\n");', line)


def translate_line(line):
    """
    Function to run when reading a single line.
    """
    commands = {
        re.compile("print\(\"([^\"]*)\"\)"): r'printf("\1\\n");'
    }
    # return parse_print(line)
    for pattern in commands:
        m = pattern.search(line)
        if m:
            return re.sub(pattern, commands[pattern], line)
    return ""


def error_check(translated_code):
    """
    Check to see if there are any erros by checking the return
    status of gcc after attempting to compile the translated_code.
    """
    tmpfilename = "hopefully_there_arent_any_other_files_with_this_name"
    tmpfile = open(tmpfilename + ".c", "w")
    tmpfile.write(translated_code)
    tmpfile.close()

    import subprocess
    p = subprocess.Popen("gcc {}.c -o {}".format(tmpfilename,
                         tmpfilename).split())
    p.communicate()

    import os
    try:
        os.remove(tmpfilename)
    except OSError:
        print("Could not generate an executable due to an error.",
              file=sys.stderr)
    os.remove(tmpfilename + ".c")

    # Success on 0
    return not p.returncode


def read_file(filename, no_whitespace=True):
    """
    Read the contents of a file into a list.
    """
    f = open(filename, "r")
    text = f.read().splitlines()
    f.close()

    if no_whitespace:
        text = filter(lambda x: x.strip() != "", text)

    return text


def get_args():
    """
    Standard arggument parser creator function.
    Import here because only using this module here.
    """
    from argparse import ArgumentParser

    parser = ArgumentParser(description="Convert python code to C code")
    parser.add_argument("file", help=".py file to translate to C.")
    parser.add_argument(
        "-s", "--indent-size", type=int, default=4,
        help="The number of spaces with which to represent each indent."
    )
    parser.add_argument(
        "-c", "--compile-check", default=False, action="store_true",
        help="Instead of printing to stdout, compile the generated code \
        and see if there are any errors."
    )

    return parser.parse_args()


def main():
    """
    Stages
    1. Setup stuff from arguments
    2. Ignore certain lines of code.
    3. Add necessary includes and main function.
    4. Actual translation.
    """
    args = get_args()
    code = read_file(args.file)

    # Setup
    Block.indent = args.indent_size
    top = Block(should_indent=False)

    # Run filtering process
    code = filter(should_keep_line, code)

    # Include includes
    top.append_blocks(includes(code))

    # Add main function
    top.append(main_func())

    # Add remaining relevant code
    for i in xrange(len(code)):
        top.last.append(StringBlock(translate_line(code[i])))

    if args.compile_check:
        return 0 if error_check(str(top)) else 1
    else:
        print(top)

    return 0


if __name__ == "__main__":
    sys.exit(main())
