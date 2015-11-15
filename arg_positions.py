#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import print_function

"""
Module for getting the positions of arguments in a function provided
in a string.

collect_offsets() and argpos() from:
http://stackoverflow.com/questions/16635254/parsing-python-function-calls-to-get-argument-positions
"""

import ast
import re


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


def parseprint(code, filename="<string>", mode="exec", **kwargs):
    """Parse some code from a string and pretty-print it."""
    node = ast.parse(code, mode=mode)   # An ode to the code
    print(ast.dump(node, **kwargs))


def collect_offsets(call_string):
    def _abs_offset(lineno, col_offset):
        current_lineno = 0
        total = 0
        for line in call_string.splitlines():
            current_lineno += 1
            if current_lineno == lineno:
                return col_offset + total
            total += len(line)

    # parse call_string with ast
    call = ast.parse(call_string).body[0].value
    # print("call: " + str(ast.parse(call_string)))
    print("")
    parseprint(call_string)
    # print(ast.parse(call_string).body[0])

    # collect offsets provided by ast
    offsets = []
    for arg in call.args:
        a = arg
        while isinstance(a, ast.BinOp):
            a = a.left
        offsets.append(_abs_offset(a.lineno, a.col_offset))
    for kw in call.keywords:
        offsets.append(_abs_offset(kw.value.lineno, kw.value.col_offset))
    if call.starargs:
        offsets.append(_abs_offset(call.starargs.lineno,
                       call.starargs.col_offset))
    if call.kwargs:
        offsets.append(_abs_offset(call.kwargs.lineno, call.kwargs.col_offset))
    offsets.append(len(call_string))
    return offsets


def argpos(call_string):
    def _find_start(prev_end, offset):
        s = call_string[prev_end:offset]
        m = re.search('(\(|,)(\s*)(.*?)$', s)
        return prev_end + m.regs[3][0]

    def _find_end(start, next_offset):
        s = call_string[start:next_offset]
        m = re.search('(\s*)$', s[:max(s.rfind(','), s.rfind(')'))])
        return start + m.start()

    offsets = collect_offsets(call_string)

    result = []

    # previous end
    end = 0
    for offset, next_offset in zip(offsets, offsets[1:]):
        start = _find_start(end, offset)
        end = _find_end(start, next_offset)
        result.append((start, end))
    return result


def parse_args(call_string):
    """
    Return a generator of arguments from the call string.
    """
    positions = argpos(call_string)
    for start, end in positions:
        yield call_string[start:end]


def split_cmd(cmd):
    """
    Split a command into different parts to be evaluated.
    """


def is_literal(expression):
    """
    Determine if a function is a literal, a literal being something
    that does not require me doing any translation.

    Just check for basic ones for now.
    """
    expression = expression.strip()

    # Addition for 2 ints
    p = re.compile("\d+\s*\+\s*\d+")
    m = p.search(expression)
    return m


def is_function(expression):
    """
    Determine if a gven expression is a function.
    I say it is a function just if it's a name followed
    by a set of parenthesis containing any args.
    Ex.
        "range(5+10)" -> True
        "len(range(5+10))" -> True
        "5+10" -> False
    """
    expression = expression.strip()

    if is_literal(expression):
        return False

    p = re.compile("^\S+\(([\s\S]*)\)$")
    m = p.search(expression)
    return bool(m)


def test(call_string):
    """
    Just print out the results found by this argument position finder.
    """
    positions = argpos(call_string)
    print(call_string)
    for p in positions:
        marker = ' ' * p[0] + '^'
        if p[1] - p[0] > 1:
            marker += ' ' * (p[1] - p[0] - 2) + '^'
        print(marker)
    print(positions)
    print(list(parse_args(call_string)))

if __name__ == "__main__":
    cmds = [
        "whatever(foo, baz(), 'puppet', 24+2, meow=3, *meowargs, **meowargs)",
        "f(1, len(document_text) - 1 - position)",
        "Foo(x=y, **kwargs)",
        "xrange(5,10,1)",
    ]
    for cmd in cmds:
        test(cmd)
