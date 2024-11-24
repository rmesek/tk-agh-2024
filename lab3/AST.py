# type: ignore
# ruff: noqa

from dataclasses import dataclass
from typing import Any


@dataclass
class Node(object):
    pass


@dataclass
class IntNum(Node):
    value: Any


@dataclass
class FloatNum(Node):
    value: Any


@dataclass
class Variable(Node):
    name: Any


@dataclass
class BinExpr(Node):
    op: Any
    left: Any
    right: Any


# ...
# fill out missing classes
# ...


class Error(Node):
    def __init__(self):
        pass
