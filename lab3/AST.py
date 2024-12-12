# type: ignore
# ruff: noqa


from dataclasses import dataclass


@dataclass
class Node:
    lineno: int


@dataclass
class StatementsNode(Node):
    statements: any


@dataclass
class StatementNode(Node):
    statement: any


@dataclass
class BreakStatement(Node):
    pass


@dataclass
class ContinueStatement(Node):
    pass


@dataclass
class ReturnStatement(Node):
    expr: any


@dataclass
class BlankStatement(Node):
    pass


@dataclass
class IntNum(Node):
    value: int


@dataclass
class FloatNum(Node):
    value: float


@dataclass
class IDNode(Node):
    name: str


@dataclass
class WhileNode(Node):
    condition: any
    body: any


@dataclass
class ForNode(Node):
    variable: any
    start: any
    end: any
    body: any


@dataclass
class IfElseNode(Node):
    condition: any
    if_body: any
    else_body: any = None


@dataclass
class AssignExpression(Node):
    left: any
    operator: str
    right: any


@dataclass
class Variable(Node):
    name: str


@dataclass
class BinExpr(Node):
    op: str
    left: any
    right: any


@dataclass
class RelationExpression(Node):
    op: str
    left: any
    right: any


@dataclass
class MatrixFuncNode(Node):
    func_name: str
    arg: any


@dataclass
class ZerosNode(MatrixFuncNode):
    pass


@dataclass
class OnesNode(MatrixFuncNode):
    pass


@dataclass
class EyeNode(MatrixFuncNode):
    pass


@dataclass
class MatrixRefNode(Node):
    id: any
    values: any


@dataclass
class IDRefNode(Node):
    value: any


@dataclass
class PrintNode(Node):
    value: any


@dataclass
class PrintRekNode(Node):
    values: any


@dataclass
class StringOfNumNode(Node):
    values: any


@dataclass
class ExpressionNode(Node):
    expr: any


@dataclass
class NegationNode(Node):
    expr: any


@dataclass
class TransposeNode(Node):
    expr: any


@dataclass
class MatrixNode(Node):
    values: any


@dataclass
class MatrixRowsNode(Node):
    values: any


@dataclass
class Error(Node):
    pass
