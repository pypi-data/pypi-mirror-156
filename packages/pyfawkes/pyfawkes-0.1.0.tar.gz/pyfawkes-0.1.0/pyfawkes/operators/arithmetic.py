import ast

class ArithmeticOperatorReplacement:
    def mutate_Add(self, node):
        yield ast.Sub()

    def mutate_Sub(self, node):
        yield ast.Add()

    def mutate_Mult(self, node):
        yield ast.Div()
        yield ast.FloorDiv()
        yield ast.Pow()

    def mutate_Div(self, node):
        yield ast.Mult()
        yield ast.FloorDiv()

    def mutate_FloorDiv(self, node):
        yield ast.Div()
        yield ast.Mult()

    def mutate_Mod(self, node):
        yield ast.Mult()

    def mutate_Pow(self, node):
        yield ast.Mult()

    def mutate_USub(self, node):
        yield ast.UAdd()

    def mutate_UAdd(self, node):
        yield ast.USub()
