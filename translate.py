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


def load_file_module(filename):
    with open(filename, "r") as py_file:
        return ast.parse(py_file.read())


#def num_type()


def translate_assign(node, output):
    """Handle assign statements.
    TODO: Handle unpacking and loading from variables.
    """
    assert isinstance(node, ast.Assign)

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
        print("{} ".format(value_type), file=output, end="")

        # Print variable names
        assert all(isinstance(target, ast.Name) and isinstance(target.ctx, ast.Store) for target in node.targets)
        print(" = ".join(target.id for target in node.targets), file=output, end="")

        # Print RHS
        print(" = {};".format(n), file=output)
    else:
        raise RuntimeError("TODO: Be sure to handle value types of {}.".format(type(value)))


def translate_bin_op(node, output):
    """Handle binary operations."""
    assert isinstance(node, ast.BinOp)

    op = node.op

    if isinstance(op, ast.Add):
        prettyparseprint(node)
        print("({} + {})".format(node.left.id, node.right.id), file=output, end="")
    else:
        raise RuntimeError("TODO: be sure to implement the {} operation.".format(op))


def translate_print(node, output):
    """Handle python2 print statement."""
    assert isinstance(node, ast.Print)

    dest = node.dest
    values = node.values

    print_str = ""
    for i, val in enumerate(values):
        if isinstance(val, ast.BinOp):
            #print_str
            print("printf({});", translate_bin_op(val, output), file=output)
        else:
            raise RuntimeError("TODO: be sure to implement the {} operation.".format(op))

    if dest is None:
        # Print to stdout
        #print(" ".join())
        pass


def translate_body(body_node, output):
    """Translate the body of a node."""
    for node in body_node:
        if isinstance(node, ast.Assign):
            translate_assign(node, output)
        elif isinstance(node, ast.Print):
            translate_print(node, output)
        else:
            prettyparseprint(node)


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
                        help="Target output filename. Defaults to stdout.")
    parser.add_argument("-v", "--verbose", action="count", default=0,
                        help="Logging verbosity.")

    # Set logging verbosity
    args = parser.parse_args()
    logging.basicConfig(format="[%(asctime)s] %(levelname)s: %(message)s",
                        stream=sys.stderr)
    if args.verbose == 1:
        LOGGER.setLevel(logging.INFO)
    elif args.verbose == 2:
        LOGGER.setLevel(logging.DEBUG)

    return args


def main():
    args = get_args()

    module_node = load_file_module(args.filename)
    translate_body(module_node.body, args.output)

    return 0


if __name__ == "__main__":
    main()

