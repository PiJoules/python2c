#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import print_function

import ast

LITERAL_NODES = [ast.Num, ast.Str, ast.List, ast.Tuple, ast.Set, ast.Dict,
                 ast.Ellipsis]


def is_literal(node):
    """
    Check if a node represents a python literal.
    """
    return any(map(lambda x: isinstance(node, x), LITERAL_NODES))


def list_to_str(list_node):
    str_rep = "["
    variables = []
    for node in list_node.elts:
        if isinstance(node, ast.Num):
            str_rep += str(node.n)
        elif isinstance(node, ast.Str):
            str_rep += "'" + str(node.s) + "'"
        elif isinstance(node, ast.List):
            str_rep, variables2add = list_to_str(node)
            variables += variables2add
        elif isinstance(node, ast.Name) and isinstance(node.ctx, ast.Load):
            str_rep += "%s"
            variables.append(node.id)
        else:
            raise Exception(
                "No support for string conversion of node of type {}"
                .format(node))
        str_rep += ", "

    if len(list_node.elts) > 0:
        str_rep = str_rep[:-2]
    str_rep += "]"
    return str_rep, variables
