#!/usr/bin/env python
# -*- coding: utf-8 -*-


class Block(object):
    """
    Class for representing a block of code/scope.

    Every child block indicates another indent in
    the returned code.
    """

    indent = 4

    def __init__(self, contents=[], should_indent=True):
        """
        contents:
            List of child blocks
        should_indent:
            Whether or not the contents of this block should
            be indented. This should ideally be only False for
            the highest level block (the one with no parent)
            blocks.
        """
        assert all(issubclass(child.__class__, Block) for child in contents)
        self.contents = contents
        self.should_indent = should_indent

    @property
    def last(self):
        return self.contents[-1]

    def append(self, block):
        """
        Append another block to this block's contents.
        """
        assert issubclass(block.__class__, Block)
        self.contents.append(block)

    def append_blocks(self, blocks):
        """
        Same as append, but for a list of blocks.
        """
        for block in blocks:
            self.append(block)

    def __str__(self):
        indentation = " "*self.indent if self.should_indent else ""
        child_contents = map(lambda x: indentation + str(x), self.contents)
        return "\n".join(child_contents)


class FunctionBlock(Block):
    """
    Block for functions.
    func_type:
        Data type to be returned by the func.
        (int, float, etc.)
    name:
        Function name
    args:
        Dict of args to include in the function.
    """
    def __init__(self, func_type, name, args, contents=[]):
        super(FunctionBlock, self).__init__(contents)
        self.func_type = func_type
        self.name = name

    def __str__(self):
        lines = ["{type} {name}(){{".format(type=self.func_type,
                                            name=self.name)]

        indentation = " "*self.indent if self.should_indent else ""
        child_contents = map(lambda x: indentation + str(x),
                             self.contents)
        lines += child_contents

        lines += [indentation + "return 0;", "}"]
        return "\n".join(lines)


class StringBlock(Block):
    """
    Block for representing a single line/string from code.
    """
    def __init__(self, contents=""):
        assert isinstance(contents, basestring)
        self.contents = contents

    def __str__(self):
        return str(self.contents)
