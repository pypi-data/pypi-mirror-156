import ast

from pyfawkes import utils


class UnaryOperatorDeletion:
    def mutate_UnaryOp(self, node):
        yield node.operand

    def mutate_NotIn(self, node):
        yield ast.In()

    def mutate_IsNot(self, node):
        yield ast.Is()


class StatementDeletion:
    def mutate_Assign(self, node):
        yield ast.Pass()

    def mutate_Return(self, node):
        yield ast.Pass()

    def mutate_Expr(self, node):
        if not utils.is_docstring(node.value):
            yield ast.Pass()
