import ast

from copy import deepcopy
from decorator import decorator

@decorator
def copy_node(mutate, self, node):
    return mutate(self, deepcopy(node, memo={id(node.parent): node.parent}))


class ConditionalOperatorNegation:
    @copy_node
    def yield_negated_test(self, node):
        node.test = ast.UnaryOp(op=ast.Not(), operand=node.test)
        yield node

    mutate_While = yield_negated_test
    mutate_If = yield_negated_test
    mutate_IfExp = yield_negated_test

    def mutate_In(self, node):
        yield ast.NotIn()


class LogicalOperatorReplacement:
    def mutate_And(self, node):
        yield ast.Or()

    def mutate_Or(self, node):
        yield ast.And()


class BitwiseOperatorReplacement:
    def yield_other_bitoperators(self, node):
        for op in [ast.BitOr, ast.BitAnd, ast.BitXor]:
            if not isinstance(node, op):
                yield op()

    mutate_BitAnd = yield_other_bitoperators
    mutate_BitOr = yield_other_bitoperators
    mutate_BitXor = yield_other_bitoperators

    def mutate_LShift(self, node):
        yield ast.RShift()

    def mutate_RShift(self, node):
        yield ast.LShift()


class ComparisonOperatorReplacement:
    def yield_other_comparisons(self, node):
        for comp in [ast.Gt, ast.Lt, ast.GtE, ast.LtE, ast.Eq, ast.NotEq]:
            if not isinstance(node, comp):
                yield comp()

    mutate_Lt = yield_other_comparisons
    mutate_Gt = yield_other_comparisons
    mutate_LtE = yield_other_comparisons
    mutate_GtE = yield_other_comparisons
    mutate_Eq = yield_other_comparisons
    mutate_NotEq = yield_other_comparisons
