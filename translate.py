#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import print_function

import re
import ast

import blocks

from block_utils import *


def prettyparseprintfile(filename, spaces=4):
    with open(filename, "r") as f:
        prettyparseprint(f.read(), spaces)


def prettyparseprint(code, spaces=4):
    node = ast.parse(code)
    text = ast.dump(node)
    indent_count = 0
    i = 0
    while i < len(text):
        c = text[i]

        if text[i:i+2] in ("()", "[]"):
            i += 1
        elif c in "([":
            indent_count += 1
            indentation = spaces*indent_count
            text = text[:i+1] + "\n" + " "*indentation + text[i+1:]
        elif c in ")]":
            indent_count -= 1
            indentation = spaces*indent_count
            text = text[:i] + "\n" + " "*indentation + text[i:]
            i += 1 + indentation

            if text[i:i+3] in ("), ", "], "):
                text = text[:i+2] + "\n" + " "*indentation + text[i+3:]
                i += indentation

        i += 1
    print(text)


def includes_from_code(code):
    """
    Return a list of #includes that are necessary to run the
    C code.
    """
    includes = []
    if any("print" in line for line in code):
        includes.append(blocks.StringBlock("#include <stdio.h>"))
        includes.append(blocks.StringBlock('#include "c_utils/utils.h"'))

    # Add a blank line for no reason
    includes.append(blocks.StringBlock())
    return includes


def main_function():
    """
    Return a standard main function block.
    """
    main_block = blocks.FunctionBlock(
        "int", "main", [
            blocks.ExprBlock("int", "argc", is_arg=True),
            blocks.ExprBlock("char", "argv", pointer_depth=1, array_depth=1,
                             is_arg=True)
        ],
        sticky_end=[blocks.StringBlock("return 0;")]
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


def evaluate_node(node, parent):
    """
    Given a node, evaluate it and adda a result the parent node.
    """
    # prettyparseprint(node)
    if isinstance(node, ast.For):
        iterator = node.target.id

        # Add unique iterator (int) that may be reused
        iterator_block = blocks.ExprBlock("int", "iter_" + str(iterator))
        if iterator_block not in parent.variables:
            parent.append_block(iterator_block)

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
            range_obj = blocks.AssignBlock(
                "Object", "temp_range_list"+str(len(parent.variables)),
                "range({},{},{})".format(start, stop, step),
                pointer_depth=1)

            # Create the getter object for the iterator.
            # This does not need ot be freed since we are just
            # redirecting a pointer.
            num_obj = blocks.AssignBlock(
                "Object", iterator,
                "list_get({}, {})"
                .format(range_obj.name, iterator_block.name),
                pointer_depth=1)

            # Create the loop, and put the range constructor before it
            # and the range destructor after it.
            range_block = blocks.ForBlock(
                iterator_block.name, "{}->length".format(range_obj.name),
                before=[range_obj], after=[range_obj.destructor()],
                sticky_front=[num_obj])

            # Add the for loop to the parent block
            parent.append_block(range_block)

            # Add the contents of the body of the for loop.
            # Filter for unecessary lines first.
            for_body = filter_body_nodes(node.body)
            for f_node in for_body:
                evaluate_node(f_node, range_block)
    elif isinstance(node, ast.Expr):
        if isinstance(node.value, ast.Call):
            if node.value.func.id == "print":
                arguments = node.value.args
                if len(arguments) == 1:
                    arg = arguments[0]
                    parent.append_block(blocks.PrintBlock(arg))
    elif isinstance(node, ast.Assign):
        targets = node.targets
        value = node.value
        if is_literal(value):
            if isinstance(value, ast.Num):
                var = value.n
                for target in targets:
                    # Make sure the target is a variable
                    # and you are storing a value
                    assert isinstance(target, ast.Name)
                    assert isinstance(target.ctx, ast.Store)
                    num_obj = blocks.AssignBlock(
                        "Object", target.id, "new_Integer({})".format(var),
                        pointer_depth=1)
                    parent.append_block(num_obj)
                    parent.prepend_sticky_end(num_obj.destructor())
            else:
                raise Exception(
                    "No support yet for loading a value from literal {}"
                    .format(value))
        else:
            raise Exception(
                "No support yet for loading a value from a non-literal")


def translate(file_, indent_size=4):
    """
    The function for actually translating the code.
    code:
        List containing lines of code.
    """
    # Setup
    with open(file_, "r") as f:
        text = f.read()
        nodes = ast.parse(text).body
        code = text.splitlines()
    blocks.Block.indent = indent_size
    top = blocks.Block(should_indent=False)

    # Run filtering process
    code = filter(should_keep_line, code)

    # Include includes
    top.append_blocks(includes_from_code(code))

    # Add main function
    main_func = main_function()
    top.append_block(main_func)

    nodes = filter_body_nodes(nodes)
    for node in nodes:
        evaluate_node(node, main_func)

    return str(top)
