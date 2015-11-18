#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import print_function


class Block(object):
    """
    Class for representing a block of code/scope.

    Every child block indicates another indent in
    the returned code.
    """

    indent = 4

    def __init__(self, contents=[], should_indent=True, sticky_front=[],
                 sticky_end=[], before=[], after=[], variables=[]):
        """
        contents:
            List of child blocks
        should_indent:
            Whether or not the contents of this block should
            be indented. This should ideally be only False for
            the highest level block (the one with no parent)
            blocks.
        sticky_front:
            Content to always appear at the front of the contents
            of the block.
        sticky_end:
            Content to always appear at the end of the contents
            of the block.
        before:
            List of blocks to appear before an instance of this block.
        after:
            List of blocks to appear after an instance of this block.
        variables:
            List of variables in the scope of this block.
        """
        assert all(issubclass(child.__class__, Block) for child in contents)
        self.contents = contents
        self.should_indent = should_indent
        self.sticky_end = sticky_end
        self.sticky_front = sticky_front
        self.before = before
        self.after = after
        self.variables = variables

    @property
    def last(self):
        return self.contents[-1]

    def append_variable(self, var):
        """
        Add a variable name to the list of variables.
        """
        if var in self.variables:
            raise Exception(
                ("Attempted to add variable '{}' in scope of {} when it "
                 "already exists: {}")
                .format(var, self.__class__, map(str, self.variables)))
        self.variables.append(var)

    def append_block(self, block):
        """
        Append another block to this block's contents.
        Add the variables within the scope of this block to the
        list of variables of the child block.
        """
        assert issubclass(block.__class__, Block)

        self.contents.append(block)
        if isinstance(block, StringBlock):
            pass
        elif isinstance(block, ExprBlock):
            self.append_variable(block)
        else:
            # block is a block that can hold variables
            for var in self.variables:
                block.append_variable(var)
            for var in block.before + block.after:
                if (isinstance(var, ExprBlock) and
                        var not in self.variables):
                    self.append_variable(var)

    def append_blocks(self, blocks):
        """
        Same as append, but for a list of blocks.
        """
        for block in blocks:
            self.append_block(block)

    def block_strings(self):
        """
        Meant to be called by __str__ to actually return the True
        formatted blocks.
        """
        indentation = " "*self.indent if self.should_indent else ""
        child_contents = []

        for content in self.sticky_front + self.contents + self.sticky_end:
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
        List of tuples containing CArguments.
    contents:
        List of blocks to fill this block with.
    """
    def __init__(self, func_type, name, args, contents=[], sticky_front=[],
                 sticky_end=[], before=[], after=[], variables=[]):
        super(FunctionBlock, self).__init__(
            contents=contents, sticky_front=sticky_front,
            sticky_end=sticky_end, before=before, after=after,
            variables=variables
        )
        self.func_type = func_type
        self.args = args
        self.name = name

        # Add the arguments
        for arg in args:
            self.append_variable(arg)

    def block_strings(self):
        """
        Meant to be called by __str__ to actually return the True
        formatted blocks.
        """
        indentation = " "*self.indent if self.should_indent else ""

        child_contents = map(str, self.before)
        child_contents += ["{type} {name}({args}){{".format(
            type=self.func_type, name=self.name,
            args=", ".join(map(str, self.args))
        )]

        for content in self.sticky_front + self.contents + self.sticky_end:
            content = content.block_strings()
            if isinstance(content, list):
                for nested_content in content:
                    child_contents.append(indentation + str(nested_content))
            else:
                child_contents.append(indentation + str(content))
        child_contents += ["}"]

        child_contents += map(str, self.after)

        return child_contents


class ForBlock(Block):
    """
    Block for for loops
    """
    def __init__(self, iterator, max_iteration, contents=[], sticky_front=[],
                 sticky_end=[], before=[], after=[], variables=[]):
        super(ForBlock, self).__init__(
            contents=contents, sticky_front=sticky_front,
            sticky_end=sticky_end, before=before, after=after,
            variables=variables
        )
        self.iterator = iterator
        self.max_iteration = max_iteration

    def block_strings(self):
        indentation = " "*self.indent if self.should_indent else ""

        child_contents = map(str, self.before)
        child_contents += [
            "for ({iterator} = 0; i < {max_iteration}; {iterator}++){{"
            .format(iterator=self.iterator, max_iteration=self.max_iteration)
        ]

        for content in self.sticky_front + self.contents + self.sticky_end:
            content = content.block_strings()
            if isinstance(content, list):
                for nested_content in content:
                    child_contents.append(indentation + str(nested_content))
            else:
                child_contents.append(indentation + str(content))
        child_contents += ["}"]
        child_contents += map(str, self.after)

        return child_contents


class ExprBlock(Block):
    """
    Class for specifically declaring a variable.
    """

    def __init__(self, data_type, name, pointer_depth=0, array_depth=0,
                 is_arg=False):
        """
        data_type:
            Data type (int, float, some typedef, etc.)
        name:
            Name of the argument
        pointer_depth:
            Essentially number of pointers to put to the left of the
            argument name when printing.
        array_depth:
            Essentially number of bracket pairs to put to the right of the
            argument name when printing.
        is_arg:
            If this block is an argument to a function, in which case, there
            should be no semicolon in the str representation of this.
        """
        # TODO: Add support for const and other qualifiers later.
        super(ExprBlock, self).__init__(should_indent=False)
        self.data_type = data_type
        self.name = name
        self.pointer_depth = pointer_depth
        self.array_depth = array_depth
        self.is_arg = is_arg

    def block_strings(self):
        return str(self)

    def __eq__(self, other):
        return self.name == other.name

    def __str__(self):
        return "{} {}{}{}{}".format(
            self.data_type, "*"*self.pointer_depth, self.name,
            "[]"*self.array_depth, "" if self.is_arg else ";")


class AssignBlock(ExprBlock):
    """
    Class for assigning a variable.
    """

    def __init__(self, data_type, name, value, pointer_depth=0, array_depth=0):
        """
        target:
            The expr block.
        value:
            The right side of the equals sign.
        """
        super(AssignBlock, self).__init__(
            data_type=data_type, name=name, pointer_depth=pointer_depth,
            array_depth=array_depth
        )
        self.value = value

    def destructor(self):
        if self.data_type == "Object":
            return StringBlock("destroy({});".format(self.name))
        else:
            raise Exception(("Attempting to call destroy on a variable that"
                             "isn't an object."))

    def __str__(self):
        return "{} {}{}{} = {};".format(
            self.data_type, "*"*self.pointer_depth, self.name,
            "[]"*self.array_depth, self.value)


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
