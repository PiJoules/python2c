#!/usr/bin/env python
from __future__ import print_function

import re


def should_ignore(line):
    """
    Determine whether or not a line should be ignored for now.
    """
    patterns_to_ingore = [
        re.compile('#!/usr/bin/env python'),
        re.compile('from __future__ import .+')
    ]
    return any(p.search(line) for p in patterns_to_ingore)


def should_keep(line):
    """
    Just the oposite of should_ignore.
    Wanted to use should_ignore in a filter function, but
    coudln't do 'code = filter(not should_ignore, code)'
    """
    return not should_ignore(line)


def parse_print(line):
    """
    Simple translation of a static string.
    """
    return re.sub(r'print\("([^"]*)"\)', r'printf("\1");', line)


def translate_line(line):
    """
    Function to run when reading a single line.
    """

    return parse_print(line)


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
    """
    from argparse import ArgumentParser

    parser = ArgumentParser(description="Convert python code to C code")
    parser.add_argument("file")

    return parser.parse_args()


def main():
    args = get_args()
    code = read_file(args.file)

    # Run filtering process
    code = filter(should_keep, code)

    for i in xrange(len(code)):
        line = code[i]
        code[i] = translate_line(line)

    print("\n".join(code))


if __name__ == "__main__":
    main()
