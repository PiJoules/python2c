#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import print_function

import re
import sys

from blocks import *
from arg_positions import prettyparseprint
import ast


def includes(code):
    """
    Return a list of #includes that are necessary to run the
    C code.
    """
    includes = []
    if any("print" in line for line in code):
        includes.append(StringBlock("#include <stdio.h>"))
        includes.append(StringBlock('#include "c_tests/Object-C/utils.h"'))

    # Add a blank line for no reason
    includes.append(StringBlock())

    return includes


def main_func():
    """
    Return a standard main function block.
    """
    main_block = FunctionBlock("int", "main", [("int", "argc"),
                               ("char", "*argv[]")])
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


def translate_line(line):
    """
    Function to run when reading a single line.
    """
    commands = {
        re.compile("print\(\"([^\"]*)\"\)"): r'printf("\1\\n");',
        # re.compile("for\s+(.+)\s+in\s+([^\:]+)\:"): r''
    }
    for pattern in commands:
        m = pattern.search(line)
        if m:
            return re.sub(pattern, commands[pattern], line)
    return ""


def evaluate(expression):
    """
    When given a function with arguments, keep recursively tracking
    what needs to get evaluated by another function and stop on reaching
    a literal or variable.
    Ex.
        range(5+10) -> evaluate("5+10") -> stop
        range(len(range(5+10))) -> evaluate("len(range(5+10))")
        -> evaluate("range(5+10)") -> evaluate("5+10") -> stop

    expression:
        Maybe the function name
    """
    pass


def translate_block(code):
    """
    If you find a line that indicates a block, create the block and
    fill it with the following lines.
    """
    pass


def error_check(translated_code):
    """
    Check to see if there are any erros by checking the return
    status of g++ after attempting to compile the translated_code.
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
        print("Successful compilation!")
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
    # code = filter(should_keep_line, code)

    # Include includes
    top.append_blocks(includes(code))

    # # Add main function
    top.append(main_func())

    # # Add remaining relevant code
    # for i in xrange(len(code)):
    #     line = code[i]
    #     top.last.append(StringBlock(translate_line(line)))

    # if args.compile_check:
    #     return 0 if error_check(str(top)) else 1
    # else:
    #     print(top)

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

    with open(args.file, "r") as f:
        nodes = ast.parse(f.read()).body

    nodes = filter_body_nodes(nodes)

    for node in nodes:
        prettyparseprint(node)
        if isinstance(node, ast.For):
            iterator = node.target.id
            top.last.append(StringBlock("int {};".format(iterator)))
            if node.iter.func.id == "range":
                if len(node.iter.args) == 1:
                    argument = node.iter.args[0]
                    if isinstance(argument, ast.BinOp):
                        if isinstance(argument.left, ast.Num) and isinstance(argument.right, ast.Num):
                            op = get_op(argument.op, argument.left.n, argument.right.n)
                            top.last.append(StringBlock("Object *temp_range_list1 = range(0,{},1);".format(op)))
                            top.last.append(ForBlock(iterator, "temp_range_list1->length"))
                for_body = filter_body_nodes(node.body)
                for f_node in for_body:
                    if isinstance(f_node, ast.Expr):
                        if isinstance(f_node.value, ast.Call):
                            if f_node.value.func.id == "print":
                                arguments = f_node.value.args
                                if len(arguments) == 1:
                                    top.last.last.append(StringBlock("Object *num_{iterator} = list_get(temp_range_list1, {iterator});".format(iterator=iterator)))
                                    top.last.last.append(StringBlock("char *num_str_{iterator} = str(num_{iterator});".format(iterator=iterator)))
                                    top.last.last.append(StringBlock('printf("%s\\n", num_str_{iterator});'.format(iterator=iterator)))
                                    top.last.last.append(StringBlock("free(num_str_{iterator});".format(iterator=iterator)))
                top.last.append(StringBlock("destroy(temp_range_list1);"))

    print(top)

    return 0


if __name__ == "__main__":
    sys.exit(main())
