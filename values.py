#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import print_function


class Value(object):
    def __init__(self, data_type, name, pointer_depth=0, array_depth=0):
        self.data_type = data_type
        self.name = name
        self.pointer_depth = pointer_depth
        self.array_depth = array_depth

    def __eq__(self, other):
        # Variables cannot be delcared twice
        return self.name == other.name


class Variable(Value):
    def __init__(self, data_type, name, meta_type=None, pointer_depth=0,
                 array_depth=0):
        super(Variable, self).__init__(
            data_type, name, pointer_depth=pointer_depth,
            array_depth=array_depth)

        # If the actual data_type is Object,
        # we may still want to know what this
        # Object represents. (string, int, etc.)
        self.meta_type = meta_type

    # def __eq__(self, other):
    #     return self.name == other.name and self.meta_type == other.meta_type

    def dict(self):
        return {
            "data_type": self.data_type,
            "name": self.name,
            "meta_type": self.meta_type,
            "pointer_depth": self.pointer_depth,
            "array_depth": self.array_depth
        }

    def __str__(self):
        return self.name


class Literal(Variable):
    def __init__(self, data_type, value):
        super(Literal, self).__init__(data_type, value)

    def __str__(self):
        if isinstance(self.name, basestring):
            return "\"" + str(self.name) + "\""
        else:
            return str(self.name)


class Argument(Variable):
    def __init__(self, data_type, name, meta_type=None, pointer_depth=0,
                 array_depth=0):
        super(Argument, self).__init__(
            data_type, name, pointer_depth=pointer_depth,
            array_depth=array_depth, meta_type=meta_type)

    def __str__(self):
        return "{} {}{}{}".format(
            self.data_type, "*" * self.pointer_depth, self.name,
            "[]" * self.array_depth)


class PassedArgument(Argument):
    def __init__(self, data_type, name, meta_type=None, pointer_depth=0,
                 array_depth=0):
        super(Argument, self).__init__(
            data_type, name, pointer_depth=pointer_depth,
            array_depth=array_depth, meta_type=meta_type)

    def __str__(self):
        return str(self.name)


class PassedLiteralArgument(PassedArgument):
    def __init__(self, data_type, name, meta_type=None, pointer_depth=0,
                 array_depth=0):
        super(Argument, self).__init__(
            data_type, name, pointer_depth=pointer_depth,
            array_depth=array_depth, meta_type=meta_type)

    def __str__(self):
        if isinstance(self.name, basestring):
            return "\"" + str(self.name) + "\""
        else:
            return str(self.name)


class Function(Value):
    def __init__(self, data_type, name, arguments, pointer_depth=0,
                 array_depth=0, return_variable=None):
        super(Function, self).__init__(
            data_type, name, pointer_depth=pointer_depth,
            array_depth=array_depth)

        assert all(map(lambda x: isinstance(x, Argument), arguments))
        self.arguments = arguments

        if return_variable:
            assert isinstance(return_variable, Variable)
        self.return_variable = return_variable

    def __str__(self):
        args = ", ".join(map(str, self.arguments))
        return "{name}({args})".format(name=self.name, args=args)
