#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import print_function

import ast
import re

import blocks
import values

from block_utils import is_literal, list_to_str


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

        if text[i:i + 2] in ("()", "[]"):
            i += 1
        elif c in "([":
            indent_count += 1
            indentation = spaces * indent_count
            text = text[:i + 1] + "\n" + " " * indentation + text[i + 1:]
        elif c in ")]":
            indent_count -= 1
            indentation = spaces * indent_count
            text = text[:i] + "\n" + " " * indentation + text[i:]
            i += 1 + indentation

            if text[i:i + 3] in ("), ", "], "):
                text = text[:i + 2] + "\n" + " " * indentation + text[i + 3:]
                i += indentation

        i += 1
    print(text)


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


def evaluate_variable_str(name, parent_block):
    str_name = name + "_str"
    var = values.Variable("char", str_name, pointer_depth=1)
    str_func = values.Function(
        "char", "str", [values.PassedArgument("Object", name)])
    str_create = blocks.AssignBlock(var, str_func)
    parent_block.append_block(str_create)


def evaluate_print(args, parent_block):
    if len(args) == 1:
        arg = args[0]
        if isinstance(arg, ast.Str):
            parent_block.append_block(
                blocks.StringBlock('printf("{}\\n");'.format(arg.s)))
        elif isinstance(arg, ast.Num):
            parent_block.append_block(
                blocks.StringBlock('printf("{}\\n");'.format(arg.n)))
        elif isinstance(arg, ast.List):
            # Need to load the variable
            # Then convert it to a string
            # Do not immediately free it since it will
            # be freed at the end of the function.
            list_str, variables = list_to_str(arg, parent_block.variables)
            if len(variables) == 0:
                parent_block.append_block(
                    blocks.StringBlock('printf("{}\\n");'.format(list_str)))
            else:
                for variable in variables:
                    evaluate_variable_str(variable, parent_block)

                joint_strings = ", ".join(map(lambda x: x + "_str", variables))
                print_block = blocks.StringBlock(
                    'printf("{}\\n", {});'.format(list_str, joint_strings))
                parent_block.append_block(print_block)
        elif isinstance(arg, ast.Name):
            # Need to load the variable
            # Then convert it to a string
            # Do not immediately free it since it will
            # be freed at the end of the function.
            name = arg.id
            str_name = arg.id + "_str"
            evaluate_variable_str(name, parent_block)

            str_print = blocks.StringBlock(
                'printf("%s\\n", {});'.format(str_name))

            parent_block.append_block(str_print)


def evaluate_assignment(targets, value, parent_block):
    if is_literal(value):
        if isinstance(value, ast.Num):
            for target in targets:
                name = target.id
                lh_var = values.Variable("Object", name, pointer_depth=1)
                arg = values.PassedArgument("Object", value.n, meta_type="int")
                rh_var = values.Function("Object", "new_Integer", [arg])
                parent_block.append_block(blocks.AssignBlock(lh_var, rh_var))
        if isinstance(value, ast.Str):
            for target in targets:
                name = target.id
                lh_var = values.Variable("Object", name, pointer_depth=1)
                lh_var.meta_type = "string"
                rh_var = values.Function(
                    "Object", "new_String",
                    [values.PassedArgument(
                        "Object", "\"" + value.s + "\"")])
                parent_block.append_block(blocks.AssignBlock(lh_var, rh_var))


def evaluate_node(node, parent_block):
    if isinstance(node, ast.Expr):
        if isinstance(node.value, ast.Call):
            func = node.value.func.id
            args = node.value.args
            ctx = node.value.func.ctx
            if func == "print" and isinstance(ctx, ast.Load):
                evaluate_print(args, parent_block)
    elif isinstance(node, ast.Assign):
        targets = node.targets
        if all(map(lambda x: isinstance(x, ast.Name), targets)):
            evaluate_assignment(targets, node.value, parent_block)
        elif len(targets) == 1 and isinstance(targets[0], ast.Tuple):
            pass


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
    top = blocks.FileBlock()

    # Run filtering process
    code = filter(should_keep_line, code)

    # Include includes
    top.append_block(blocks.IncludeBlock("c_utils/utils.h"))
    top.append_block(blocks.EmptyBlock())

    # Add main function
    argc = values.Argument("int", "argc")
    argv = values.Argument("char", "argv", pointer_depth=1, array_depth=1)
    main_func = values.Function("int", "main", [argc, argv])
    main_func.return_variable = "0"
    main_func_block = blocks.FunctionBlock(main_func)
    top.append_block(main_func_block)

    nodes = filter_body_nodes(nodes)
    for node in nodes:
        evaluate_node(node, main_func_block)

    return str(top)
