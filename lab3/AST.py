# type: ignore
# ruff: noqa

from dataclasses import dataclass
from typing import List


@dataclass
class Node:
    pass


@dataclass
class IntNum(Node):
    value: int


@dataclass
class FloatNum(Node):
    value: float


@dataclass
class String(Node):
    value: str


@dataclass
class Variable(Node):
    name: str


@dataclass
class BinExpr(Node):
    op: str
    left: Node
    right: Node


@dataclass
class Assignment(Node):
    op: str
    variable: Variable
    expression: Node


@dataclass
class MatrixFunction(Node):
    function: str
    argument: Node


@dataclass
class Matrix(Node):
    rows: List[List[Node]]


@dataclass
class MatrixAccess(Node):
    variable: Variable
    indices: List[Node]


@dataclass
class UnaryExpr(Node):
    op: str
    expr: Node


@dataclass
class Transpose(Node):
    expr: Node


@dataclass
class Condition(Node):
    op: str
    left: Node
    right: Node


@dataclass
class Print(Node):
    expressions: List[Node]


@dataclass
class Error(Node):
    message: str = ""
