#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function

import logging
import ast
import sys

from utils import prettyparseprint

LOGGER = logging.getLogger(__name__)


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


def load_file_module(filename):
    with open(filename, "r") as py_file:
        return ast.parse(py_file.read())


def translate_body(body_node, output):
    for node in body_node:
        pass


def main():
    args = get_args()

    module_node = load_file_module(args.filename)
    prettyparseprint(module_node)

    return 0


if __name__ == "__main__":
    main()

