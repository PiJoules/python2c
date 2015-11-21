#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import print_function

import values


class Block(object):
    indent = 4

    def __init__(self):
        pass

    def block_strings(self):
        return []

    def __str__(self):
        return "\n".join(self.block_strings())


class BodyBlock(Block):
    def __init__(self, functions=None, variables=None):
        if functions:
            assert all(map(lambda x: isinstance(x, values.Function),
                           functions))
        self.functions = functions or []

        if variables:
            assert all(map(lambda x: isinstance(x, values.Variable),
                           variables))
        self.variables = variables or []

    def contains_function(self, func):
        assert isinstance(func, values.Function)
        return func in self.functions

    def contains_variable(self, var):
        assert isinstance(var, values.Variable)
        return var in self.variables


class InlineBlock(Block):
    def __init__(self):
        pass


class StringBlock(InlineBlock):
    def __init__(self, contents=""):
        self.contents = contents

    def block_strings(self):
        return [self.contents]


class EmptyBlock(StringBlock):
    """
    Just an empty line.
    """
    def __init__(self):
        super(EmptyBlock, self).__init__("")


class IncludeBlock(InlineBlock):
    def __init__(self, libname):
        self.libname = libname

    def block_strings(self):
        return ["#include \"{}\"".format(self.libname)]


class AssignBlock(InlineBlock):
    def __init__(self, lh_var, rh_var):
        assert isinstance(lh_var, values.Value)
        assert isinstance(rh_var, values.Value)
        self.lh_var = lh_var
        self.rh_var = rh_var

    def block_strings(self):
        lh_var = self.lh_var
        rh_var = self.rh_var
        return ["{} {}{}{} = {};".format(
            lh_var.data_type, "*" * lh_var.pointer_depth, lh_var.name,
            "[]" * lh_var.array_depth, str(rh_var))]


class ReassignBlock(AssignBlock):
    def __init__(self, lh_var, rh_var):
        assert isinstance(lh_var, values.Value)
        assert isinstance(rh_var, values.Value)
        self.lh_var = lh_var
        self.rh_var = rh_var

    def block_strings(self):
        lh_var = self.lh_var
        rh_var = self.rh_var
        return [
            "{}({});".format(
                "destroy" if lh_var.data_type == "Object" else "free",
                lh_var.name),
            "{} = {};".format(lh_var.name, str(rh_var))
        ]


class FunctionBlock(BodyBlock):
    def __init__(self, function, variables=None, contents=None,
                 functions=None):
        super(FunctionBlock, self).__init__(functions=functions)

        assert isinstance(function, values.Function)
        self.function = function

        if contents:
            assert all(map(lambda x: isinstance(x, Block), contents))
        self.contents = contents or []

    def block_strings(self):
        if self.function.data_type != "void":
            # Check that a return value exists
            assert self.function.return_variable

        indentation = " " * self.indent
        blocks = [self.function.data_type + " " + str(self.function) + "{"]

        for block in self.contents:
            for block_str in block.block_strings():
                blocks.append(indentation + str(block_str))

        blocks += map(lambda x: "{}{}({});".format(indentation,
                      "destroy" if x.data_type == "Object" else "free", x),
                      self.variables)
        blocks += ["{}return {};"
                   .format(indentation, self.function.return_variable)]
        blocks += ["}"]
        return blocks

    def append_block(self, block):
        if isinstance(block, FunctionBlock):
            self.contents.append(block)
            self.functions.append(block.function)
        elif isinstance(block, AssignBlock):
            if self.contains_variable(block.lh_var):
                self.contents.append(ReassignBlock(block.lh_var, block.rh_var))
            else:
                self.contents.append(block)
                # if block.lh_var.data_type == "Object":
                self.variables.append(block.lh_var)
        elif isinstance(block, InlineBlock):
            self.contents.append(block)


class FileBlock(Block):
    """
    Block representing a whole file.
    Every block goes in here.
    The only blocks that should be allowed in here are
    - FunctionBlocks
    - IncludeBlocks

    Do not allow globals.
    """

    ALLOWED_CONTENTS = (FunctionBlock, IncludeBlock, EmptyBlock)

    def __init__(self):
        self.contents = []  # Contains only FunctionBlocks or IncludeBlocks
        self.functions = []  # Contains only Functions

    def append_block(self, block):
        assert any(map(lambda x: isinstance(block, x), self.ALLOWED_CONTENTS))
        self.contents.append(block)

        if isinstance(block, FunctionBlock):
            self.functions.append(block.function)

    def block_strings(self):
        blocks = []

        for block in self.contents:
            for block_str in block.block_strings():
                blocks.append(str(block_str))

        return blocks
