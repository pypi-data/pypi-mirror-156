import ast
from numbers import Real

from pyfawkes import utils


class NumberReplacement:
    def mutate_Constant(self, node):
        if isinstance(node.value, Real):
            yield ast.Constant(value=node.value + 1)
            yield ast.Constant(value=node.value - 1)
            yield ast.Constant(value=-node.value)
            yield ast.Constant(value=0)
            yield ast.Constant(value=1)


class StringReplacement:
    def mutate_Constant(self, node):
        if isinstance(node.value, str) and not utils.is_docstring(node):
            yield ast.Constant(value="a" if node.value != "a" else "b")
            if node.value:
                yield ast.Constant(value="")
