# type: ignore
# ruff: noqa

import AST


def addToClass(cls):
    def decorator(func):
        setattr(cls, func.__name__, func)
        return func

    return decorator


class TreePrinter:
    @addToClass(AST.Node)
    def printTree(self, indent=0):
        raise Exception("printTree not defined in class " + self.__class__.__name__)

    @addToClass(AST.IntNum)
    def printTree(self, indent=0):
        print("|  " * indent + str(self.value))

    @addToClass(AST.FloatNum)
    def printTree(self, indent=0):
        print("|  " * indent + str(self.value))

    @addToClass(AST.String)
    def printTree(self, indent=0):
        print("|  " * indent + self.value)

    @addToClass(AST.Variable)
    def printTree(self, indent=0):
        print("|  " * indent + self.name)

    @addToClass(AST.BinExpr)
    def printTree(self, indent=0):
        print("|  " * indent + self.op)
        self.left.printTree(indent + 1)
        self.right.printTree(indent + 1)

    @addToClass(AST.Assignment)
    def printTree(self, indent=0):
        print("|  " * indent + self.op)
        self.variable.printTree(indent + 1)
        self.expression.printTree(indent + 1)

    @addToClass(AST.MatrixFunction)
    def printTree(self, indent=0):
        print("|  " * indent + self.function)
        self.argument.printTree(indent + 1)

    @addToClass(AST.Matrix)
    def printTree(self, indent=0):
        print("|  " * indent + "MATRIX")
        for row in self.rows:
            print("|  " * (indent + 1) + "VECTOR")
            for expr in row:
                expr.printTree(indent + 2)

    @addToClass(AST.MatrixAccess)
    def printTree(self, indent=0):
        print("|  " * indent + "REF")
        self.variable.printTree(indent + 1)
        for index in self.indices:
            index.printTree(indent + 1)

    @addToClass(AST.UnaryExpr)
    def printTree(self, indent=0):
        print("|  " * indent + self.op)
        self.expr.printTree(indent + 1)

    @addToClass(AST.Transpose)
    def printTree(self, indent=0):
        print("|  " * indent + "TRANSPOSE")
        self.expr.printTree(indent + 1)

    @addToClass(AST.Condition)
    def printTree(self, indent=0):
        print("|  " * indent + self.op)
        self.left.printTree(indent + 1)
        self.right.printTree(indent + 1)

    @addToClass(AST.Print)
    def printTree(self, indent=0):
        print("|  " * indent + "PRINT")
        for expr in self.expressions:
            expr.printTree(indent + 1)

    @addToClass(AST.Error)
    def printTree(self, indent=0):
        print("|  " * indent + f"Error: {self.message}")
