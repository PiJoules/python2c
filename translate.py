#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function

import logging
import ast
import sys

from utils import prettyparseprint

LOGGER = logging.getLogger(__name__)

INT_TYPE = "int"
FLOAT_TYPE = "float"
LONG_TYPE = "long"
DEFAULT_INDENT = "    "
SYSTEM_HEADERS = (
    "stdio.h",
    "stdlib.h",
)


def load_file_module(filename):
    with open(filename, "r") as py_file:
        return ast.parse(py_file.read())


def add_headers(headers, start_wrapper, end_wrapper):
    return "\n".join("#include {}{}{}".format(start_wrapper, h, end_wrapper) for h in headers) + "\n"


def add_system_headers():
    return add_headers(SYSTEM_HEADERS, "<", ">")


def add_indented(line, indent_count, indent):
    """Return a line with indentation added."""
    return indent_count * indent + line


def translate_assign(node):
    """Handle assign statements.
    TODO: Handle unpacking and loading from variables.
    """
    assert isinstance(node, ast.Assign)

    result = ""
    value = node.value
    if isinstance(value, ast.Num):
        # Print type first
        n = value.n
        if isinstance(n, int):
            value_type = "int"
        elif isinstance(n, float):
            value_type = "float"
        elif isinstance(n, long):
            value_type = "long"
        else:
            raise RuntimeError("Unknown Num type '{}'.".format(type(n)))
        result += "{} ".format(value_type)

        # Print variable names
        assert all(isinstance(target, ast.Name) and isinstance(target.ctx, ast.Store) for target in node.targets)
        result += " = ".join(target.id for target in node.targets)

        # Print RHS
        result += " = {};\n".format(n)
    else:
        raise RuntimeError("TODO: Be sure to handle value types of {}.".format(type(value)))

    return result


def translate_bin_op(node):
    """Handle binary operations."""
    assert isinstance(node, ast.BinOp)

    op = node.op

    result = ""
    if isinstance(op, ast.Add):
        result += "({} + {})".format(node.left.id, node.right.id)
    else:
        raise RuntimeError("TODO: be sure to implement the {} operation.".format(op))

    return result


def translate_print(node):
    """Handle python2 print statement."""
    assert isinstance(node, ast.Print)

    dest = node.dest
    values = node.values

    str_literal = ""
    str_values = []
    for i, val in enumerate(values):
        if isinstance(val, ast.BinOp):
            str_literal += "%d"
            str_values.append(translate_bin_op(val))
        else:
            raise RuntimeError("TODO: be sure to implement the {} operation.".format(op))

    if dest is not None:
        # Not printing to stdout
        raise RuntimeError("TODO: Implement logic for when printing to stream other than stdout.")

    result = "printf(\"{literal}\\n\"{values});\n".format(
        literal=str_literal,
        values="" if not str_values else ", {}".format(", ".join(str_values))
    )

    return result


def translate_return(return_node):
    assert isinstance(return_node, ast.Return)
    return "return {};".format(return_node.value.n)


def translate_function(func_node):
    assert isinstance(func_node, ast.FunctionDef)

    name = func_node.name
    args = func_node.args.args
    if name == "main" and len(args) == 2 and args[0].id == "argc" and args[1].id == "argv":
        result = "int main(int argc, char* argv){{\n{}\n}}".format(translate_body(func_node.body, indent_count=1))
        return result

    raise RuntimeError("TODO: Implement logic for creating function.")


def translate_body(body_list, indent_count=0, indent=DEFAULT_INDENT):
    """Translate the body of a node."""
    result = ""
    for node in body_list:
        if isinstance(node, ast.Assign):
            result += add_indented(translate_assign(node), indent_count, indent)
        elif isinstance(node, ast.Print):
            result += add_indented(translate_print(node), indent_count, indent)
        elif isinstance(node, ast.FunctionDef):
            result += add_indented(translate_function(node), indent_count, indent)
        elif isinstance(node, ast.Return):
            result += add_indented(translate_return(node), indent_count, indent)
        else:
            raise RuntimeError("Unknown node in body node: {}".format(node))
    return result


def filename_to_file(filename):
    from argparse import ArgumentError
    try:
        return open(filename, "w")
    except OSError as e:
        raise ArgumentError("Unable to open file '{}': {}".format(filename, e))


def get_args():
    from argparse import ArgumentParser
    parser = ArgumentParser()

    parser.add_argument("filename", help="Python source file.")
    parser.add_argument("-o", "--output", default=sys.stdout,
                        type=filename_to_file,
                        help="Target output filename. Defaults to stdout stream if not provided.")
    parser.add_argument("--ast", default=False, action="store_true",
                        help="Print the ast of the file.")
    parser.add_argument("-v", "--verbose", action="count", default=0,
                        help="Logging verbosity.")

    # Set logging verbosity
    args = parser.parse_args()
    logging.basicConfig(format="[%(asctime)s] %(levelname)s: %(message)s",
                        stream=sys.stderr)
    if args.verbose == 1:
        LOGGER.setLevel(logging.INFO)
    elif args.verbose >= 2:
        LOGGER.setLevel(logging.DEBUG)

    return args


def main():
    args = get_args()

    module_node = load_file_module(args.filename)

    if args.ast:
        prettyparseprint(module_node)
        return 0

    result = add_system_headers()
    result += "\n"
    result += translate_body(module_node.body)
    print(result)

    return 0


if __name__ == "__main__":
    main()

