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


def get_variable(var_name, variables):
    for var in variables:
        if var.name == var_name:
            return var
    return None


def list_to_str(list_node, parent_variables):
    str_rep = "["
    variables = []
    for node in list_node.elts:
        if isinstance(node, ast.Num):
            str_rep += str(node.n)
        elif isinstance(node, ast.Str):
            str_rep += "'" + str(node.s) + "'"
        elif isinstance(node, ast.List):
            str_rep2add, variables2add = list_to_str(node, parent_variables)
            str_rep += str_rep2add
            variables += variables2add
        elif isinstance(node, ast.Name) and isinstance(node.ctx, ast.Load):
            var = get_variable(node.id, parent_variables)
            if not var:
                raise Exception(
                    "Could not find corresponding variable in {} for name {}"
                    .format(parent_variables, node.id))
            if var.meta_type == "string":
                str_rep += "'%s'"
            elif var.meta_type == "int":
                str_rep += "%s"
            else:
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
