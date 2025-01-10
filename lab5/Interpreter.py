# type: ignore
# ruff: noqa

import AST
from Memory import *
from Exceptions import *
from visit import *
import sys

sys.setrecursionlimit(10000)


def mat_add(matrix1, matrix2):
    for row in range(len(matrix1)):
        if isinstance(matrix1[0], list):
            for col in range(len(matrix1[0])):
                matrix1[row][col] += matrix2[row][col]
        else:
            matrix1[row] += matrix2[row]
    return matrix1


def mat_sub(matrix1, matrix2):
    for row in range(len(matrix1)):
        if isinstance(matrix1[0], list):
            for col in range(len(matrix1[0])):
                matrix1[row][col] -= matrix2[row][col]
        else:
            matrix1[row] -= matrix2[row]
    return matrix1


def mat_mul(matrix1, matrix2):
    for row in range(len(matrix1)):
        if isinstance(matrix1[0], list):
            for col in range(len(matrix1[0])):
                matrix1[row][col] *= matrix2[row][col]
        else:
            matrix1[row] *= matrix2[row]
    return matrix1


def mat_div(matrix1, matrix2):
    for row in range(len(matrix1)):
        if isinstance(matrix1[0], list):
            for col in range(len(matrix1[0])):
                matrix1[row][col] /= matrix2[row][col]
        else:
            matrix1[row] /= matrix2[row]
    return matrix1


def transpose(matrix):
    return [[matrix[j][i] for j in range(len(matrix))] for i in range(len(matrix[0]))]


operations = {
    "+": lambda x, y: x + y,
    "-": lambda x, y: x - y,
    "*": lambda x, y: x * y,
    "/": lambda x, y: x / y,
    "<": lambda x, y: x < y,
    ">": lambda x, y: x > y,
    "<=": lambda x, y: x <= y,
    ">=": lambda x, y: x >= y,
    "==": lambda x, y: x == y,
    "!=": lambda x, y: x != y,
    ".+": lambda x, y: mat_add(x, y),
    ".-": lambda x, y: mat_sub(x, y),
    ".*": lambda x, y: mat_mul(x, y),
    "./": lambda x, y: mat_div(x, y),
}


class Interpreter(object):
    @on("node")
    def visit(self, node):
        pass

    @when(AST.InstrOrEmpty)
    def visit(self, node: AST.Instructions):
        self.memory = MemoryStack()
        self.memory.push("global")
        node.instructions.accept(self)

    @when(AST.Instructions)
    def visit(self, node: AST.Instructions):
        for instruction in node.instructions:
            instruction.accept(self)

    @when(AST.BinExpr)
    def visit(self, node: AST.BinExpr):
        left_value = node.left.accept(self)
        right_value = node.right.accept(self)
        return operations[node.op](left_value, right_value)

    @when(AST.Unary)
    def visit(self, node: AST.Unary):
        r1 = node.expr.accept(self)
        if node.operation == "TRANSPOSE":
            return transpose(r1)
        else:
            return -r1

    @when(AST.Id)
    def visit(self, node: AST.Id):
        return self.memory.get(node.id)

    @when(AST.IntNum)
    def visit(self, node: AST.IntNum):
        return int(node.intnum)

    @when(AST.FloatNum)
    def visit(self, node: AST.FloatNum):
        return float(node.floatnum)

    @when(AST.String)
    def visit(self, node: AST.String):
        return str(node.string)

    @when(AST.If)
    def visit(self, node: AST.If):
        condition = node.cond.accept(self)
        if condition:
            self.memory.push("if")
            try:
                if isinstance(node.if_body, AST.Instructions):
                    node.if_body.accept(self)
                else:
                    for instruction in node.if_body:
                        instruction.accept(self)
            except BreakException as e:
                raise e
            except ReturnValueException as e:
                raise e
            finally:
                self.memory.pop()
        else:
            if node.else_body is not None:
                self.memory.push("else")
                try:
                    node.else_body.accept(self)
                except BreakException as e:
                    raise e
                except ReturnValueException as e:
                    raise e
                finally:
                    self.memory.pop()

    @when(AST.While)
    def visit(self, node: AST.While):
        self.memory.push("while")
        while node.cond.accept(self):
            try:
                if isinstance(node.body, list):
                    for instruction in node.body:
                        instruction.accept(self)
                else:
                    node.body.accept(self)
            except ContinueException:
                continue
            except BreakException:
                break
        self.memory.pop()

    @when(AST.For)
    def visit(self, node: AST.For):
        iterator = node.id
        start_value = node.cond_start.accept(self)
        end_value = node.cond_end.accept(self)
        self.memory.push("for")
        self.memory.set(iterator.id, start_value)
        while self.memory.get(iterator.id) <= end_value:
            try:
                if isinstance(node.body, list):
                    for instruction in node.body:
                        instruction.accept(self)
                else:
                    node.body.accept(self)
            except ContinueException:
                continue
            except BreakException:
                break
            finally:
                self.memory.set(iterator.id, self.memory.get(iterator.id) + 1)
        self.memory.pop()

    @when(AST.Return)
    def visit(self, node: AST.Return):
        raise ReturnValueException(node.expr.accept(self))

    @when(AST.Break)
    def visit(self, node: AST.Break):
        raise BreakException()

    @when(AST.Continue)
    def visit(self, node: AST.Continue):
        raise ContinueException()

    @when(AST.Print)
    def visit(self, node: AST.Print):
        to_print = [element.accept(self) for element in node.printargs]
        print(*to_print, sep=" ")

    @when(AST.AssignOp)
    def visit(self, node: AST.AssignOp):
        if not isinstance(node.left, AST.Variable):
            if node.op == "=":
                self.memory.set(node.left.id, node.right.accept(self))
            else:
                self.memory.set(node.left.id, operations[node.op[0]](self.memory.get(node.left.id), node.right.accept(self)))
        else:
            matrix = self.memory.get(node.left.id.id)
            if isinstance(node.left.index[0], tuple):
                row_indices = [i for i in range(node.left.index[0][0].accept(self), node.left.index[0][1].accept(self))]
            else:
                row_indices = [node.left.index[0].accept(self)]
            if isinstance(node.left.index[1], tuple):
                col_indices = [i for i in range(node.left.index[1][0].accept(self), node.left.index[1][1].accept(self))]
            else:
                col_indices = [node.left.index[1].accept(self)]
            if node.op == "=":
                for row in row_indices:
                    for col in col_indices:
                        matrix[col][row] = node.right.accept(self)
            else:
                for row in row_indices:
                    for col in col_indices:
                        matrix[col][row] = operations[node.op[0]](matrix[col][row], node.right.accept(self))
            self.memory.set(node.left.id.id, matrix)

    @when(AST.Vector)
    def visit(self, node: AST.Vector):
        return [element.accept(self) for element in node.vector]

    @when(AST.Variable)
    def visit(self, node: AST.Variable):
        matrix = self.memory.get(node.id.id)

        x = node.index[0].accept(self)
        y = node.index[1].accept(self)

        return matrix[x][y]

    @when(AST.MatrixFunc)
    def visit(self, node: AST.MatrixFunc):
        func = node.func
        args = [dim.accept(self) for dim in node.dims]
        if func == "zeros":
            if len(args) == 2:
                return [[0 for _ in range(args[0])] for _ in range(args[1])]
            else:
                return [0 for _ in range(args[0])]
        elif func == "ones":
            if len(args) == 2:
                return [[1 for _ in range(args[0])] for _ in range(args[1])]
            else:
                return [1 for _ in range(args[0])]
        elif func == "eye":
            if len(args) == 2:
                return [[1 if i == j else 0 for i in range(args[0])] for j in range(args[0])]
            else:
                return [1 for _ in range(args[0])]
