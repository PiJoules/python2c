#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import print_function

import re
import sys
import ast
import os
import subprocess

from blocks import *
# from ctypes import *

from arg_positions import prettyparseprint


def includes_from_code(code):
    """
    Return a list of #includes that are necessary to run the
    C code.
    """
    includes = []
    if any("print" in line for line in code):
        includes.append(StringBlock("#include <stdio.h>"))
        includes.append(StringBlock('#include "c_utils/utils.h"'))

    # Add a blank line for no reason
    includes.append(StringBlock())
    return includes


def main_function():
    """
    Return a standard main function block.
    """
    main_block = FunctionBlock(
        "int", "main", [
            ExprBlock("int", "argc", is_arg=True),
            ExprBlock("char", "argv", pointer_depth=1, array_depth=1,
                      is_arg=True)
        ],
        sticky_end=[StringBlock("return 0;")]
    )
    return main_block


def should_ignore_line(line):
    """
    Determine whether or not a line should be ignored for now.
    """
    patterns_to_ingore = [
        re.compile('#!/usr/bin/env python'),
        re.compile('from __future__ import .+'),
        re.compile('^#[\s\S]*'),
        re.compile('^\s+$')
    ]
    return any(p.search(line) for p in patterns_to_ingore)


def should_keep_line(line):
    """
    Just the oposite of should_ignore_line.
    Wanted to use should_ignore_line in a filter function, but
    coudln't do 'code = filter(not should_ignore_line, code)'
    """
    return not should_ignore_line(line)


def filter_body_nodes(body):
    ignored_nodes = [ast.ImportFrom]
    nodes = []
    for node in body:
        if any(map(lambda x: isinstance(node, x), ignored_nodes)):
            continue
        elif isinstance(node, ast.Expr) and isinstance(node.value, ast.BinOp):
            continue
        elif isinstance(node, ast.Expr) and isinstance(node.value, ast.Call):
            if isinstance(node.value.func.ctx, ast.Load):
                if node.value.func.id != "print":
                    continue
        nodes.append(node)
    return nodes


def get_op(op, arg1, arg2):
    if isinstance(op, ast.Add):
        return "{} + {}".format(arg1, arg2)
    elif isinstance(op, ast.Sub):
        return "{} - {}".format(arg1, arg2)
    elif isinstance(op, ast.Mult):
        return "{} * {}".format(arg1, arg2)
    elif isinstance(op, ast.Div) or isinstance(op, ast.FloorDiv):
        return "{} / {}".format(arg1, arg2)
    elif isinstance(op, ast.Mod):
        return "{} % {}".format(arg1, arg2)
    elif isinstance(op, ast.pow):
        return "pow((double){}, (double){})".format(arg1, arg2)
    elif isinstance(op, ast.LShift):
        return "{} << {}".format(arg1, arg2)
    elif isinstance(op, ast.RShift):
        return "{} >> {}".format(arg1, arg2)
    elif isinstance(op, ast.BitOr):
        return "{} | {}".format(arg1, arg2)
    elif isinstance(op, ast.BitXor):
        return "{} ^ {}".format(arg1, arg2)
    elif isinstance(op, ast.BitAnd):
        return "{} & {}".format(arg1, arg2)
    raise Exception("Could not identify operator " + str(op))


def handle_op_node(node):
    if isinstance(node, ast.BinOp):
        if isinstance(node.left, ast.Num) and isinstance(node.right, ast.Num):
            return get_op(node.op, node.left.n, node.right.n)
    elif isinstance(node, ast.Num):
        return node.n
    raise Exception("Could not identify node op")


def error_check_c(translated_code, execute=False):
    """
    Check to see if there are any errors by checking the return
    status of gcc after attempting to compile the translated_code.
    """
    tmpfilename = "hopefully_there_arent_any_other_files_with_this_name"
    tmpfile = open(tmpfilename + ".c", "w")
    tmpfile.write(translated_code)
    tmpfile.close()

    p = subprocess.Popen("gcc {}.c c_utils/*.c -o {}".format(tmpfilename,
                         tmpfilename), shell=True)
    p.communicate()

    if os.path.exists(tmpfilename):
        if execute:
            print(subprocess.check_output(["./" + tmpfilename]), end="")
        else:
            print("Successful compilation!")
        os.remove(tmpfilename)
    else:
        print("Could not generate an executable due to an error.",
              file=sys.stderr)
    os.remove(tmpfilename + ".c")

    # Success on 0 (return True)
    return not p.returncode


def error_check_python(filename):
    """
    Check to see if there are any errors by checking the return
    status of python after attempting to interpret the code.
    """
    with open(os.devnull, "w") as devnull:
        p = subprocess.Popen("python {}".format(filename).split(),
                             stdout=devnull)
        p.communicate()
        if p.returncode:
            print("Coulf not interpret python code due to an error.",
                  file=sys.stderr)

    # Success on 0 (return True)
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
    parser.add_argument(
        "-e", "--execute", default=False, action="store_true",
        help="Instead of translating the code and spitting to stdout, \
        immediately compile and execute the translated code. This does \
        not generate any files or print to stdout."
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

    if not error_check_python(args.file):
        return 1

    # Setup
    Block.indent = args.indent_size
    top = Block(should_indent=False)

    # Run filtering process
    code = filter(should_keep_line, code)

    # Include includes
    top.append_blocks(includes_from_code(code))

    # Add main function
    main_func = main_function()
    top.append_block(main_func)

    with open(args.file, "r") as f:
        nodes = ast.parse(f.read()).body

    nodes = filter_body_nodes(nodes)

    for node in nodes:
        # prettyparseprint(node)
        if isinstance(node, ast.For):
            iterator = node.target.id

            # Add unique iterator (int) that may be reused
            iterator_block = ExprBlock("int", iterator)
            if iterator_block not in main_func.variables:
                main_func.append_block(ExprBlock("int", iterator))

            if node.iter.func.id == "range":
                # Create a new list to be immediately used then destroyed.
                # First find the appropriate parameters for the C range func.
                if len(node.iter.args) == 1:
                    start = 0
                    stop = handle_op_node(node.iter.args[0])
                    step = 1
                elif len(node.iter.args) == 2:
                    start = handle_op_node(node.iter.args[0])
                    stop = handle_op_node(node.iter.args[1])
                    step = 1
                elif len(node.iter.args) == 3:
                    start = handle_op_node(node.iter.args[0])
                    stop = handle_op_node(node.iter.args[1])
                    step = handle_op_node(node.iter.args[2])
                else:
                    raise Exception(
                        "Invalid number of arguments found for range")

                # Create the range
                range_obj = AssignBlock(
                    "Object", "temp_range_list"+str(len(main_func.variables)),
                    "range({},{},{})".format(start, stop, step),
                    pointer_depth=1)

                # Create the getter object for the iterator.
                # This does not need ot be freed since we are just
                # redirecting a pointer.
                num_obj = AssignBlock(
                    "Object", "iter_" + iterator,
                    "list_get({}, {})"
                    .format(range_obj.name, iterator),
                    pointer_depth=1)

                # Create the loop, and put the range constructor before it
                # and the range destructor after it.
                # For some reason, the variables flag is populated with
                # the same ones added to the last ForBlock in the previous
                # iteration. Not including the variables=[] will raise this
                # error again.
                range_block = ForBlock(
                    iterator, "{}->length".format(range_obj.name),
                    before=[range_obj], after=[range_obj.destructor()],
                    sticky_front=[num_obj],
                    variables=[])

                # Add the contents of the body of the for loop.
                # Filter for unecessary lines first.
                for_body = filter_body_nodes(node.body)
                for f_node in for_body:
                    if isinstance(f_node, ast.Expr):
                        if isinstance(f_node.value, ast.Call):
                            if f_node.value.func.id == "print":
                                arguments = f_node.value.args
                                if len(arguments) == 1:
                                    # TODO: Actually handle the contents of
                                    # the contents later instead of just
                                    # hardcoding it
                                    range_block.append_block(StringBlock("char *{iterator}_str = str({iterator});".format(iterator=num_obj.name)))
                                    range_block.append_block(StringBlock('printf("%s\\n", {iterator}_str);'.format(iterator=num_obj.name)))
                                    range_block.append_block(StringBlock("free({iterator}_str);".format(iterator=num_obj.name)))

                # Add the for loop to the parent block
                main_func.append_block(range_block)

    if args.compile_check:
        return 0 if error_check_c(str(top)) else 2
    elif args.execute:
        return 0 if error_check_c(str(top), True) else 2
    else:
        print(top)

    return 0


if __name__ == "__main__":
    sys.exit(main())
