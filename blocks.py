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

    def block_strings(self):
        """
        Meant to be called by __str__ to actually return the True
        formatted blocks.
        """
        indentation = " "*self.indent if self.should_indent else ""
        child_contents = []
        for content in self.contents:
            content = content.block_strings()
            if isinstance(content, list):
                for nested_content in content:
                    child_contents.append(indentation + str(nested_content))
            else:
                child_contents.append(indentation + str(content))
        return child_contents

    def __str__(self):
        return "\n".join(self.block_strings())


class FunctionBlock(Block):
    """
    Block for functions.
    func_type:
        Data type to be returned by the func.
        (int, float, etc.)
    name:
        Function name
    args:
        List of tuples containing args (argtype, argname).
    contents:
        List of blocks to fill this block with.
    """
    def __init__(self, func_type, name, args, contents=[]):
        super(FunctionBlock, self).__init__(contents)
        self.func_type = func_type
        self.args = args
        self.name = name

    def block_strings(self):
        """
        Meant to be called by __str__ to actually return the True
        formatted blocks.
        """
        indentation = " "*self.indent if self.should_indent else ""
        child_contents = ["{type} {name}({args}){{".format(
            type=self.func_type, name=self.name,
            args=", ".join(["{} {}".format(argtype, argname)
                            for argtype, argname in self.args])
        )]
        for content in self.contents:
            content = content.block_strings()
            if isinstance(content, list):
                for nested_content in content:
                    child_contents.append(indentation + str(nested_content))
            else:
                child_contents.append(indentation + str(content))
        child_contents += [indentation + "return 0;", "}"]
        return child_contents


class ForBlock(Block):
    """
    Block for for loops
    """
    def __init__(self, iterator, max_iteration, contents=[]):
        super(ForBlock, self).__init__(contents)
        self.iterator = iterator
        self.max_iteration = max_iteration

    def block_strings(self):
        indentation = " "*self.indent if self.should_indent else ""
        child_contents = [
            "for ({iterator} = 0; i < {max_iteration}; {iterator}++){{"
            .format(iterator=self.iterator, max_iteration=self.max_iteration)
        ]
        for content in self.contents:
            content = content.block_strings()
            if isinstance(content, list):
                for nested_content in content:
                    child_contents.append(indentation + str(nested_content))
            else:
                child_contents.append(indentation + str(content))
        child_contents += ["}"]
        return child_contents


class StringBlock(Block):
    """
    Block for representing a single line/string from code.
    """
    def __init__(self, contents=""):
        assert isinstance(contents, basestring)
        self.contents = contents

    def block_strings(self):
        return str(self.contents)

    def __str__(self):
        return str(self.contents)
