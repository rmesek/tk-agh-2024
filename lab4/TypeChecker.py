# type: ignore
# ruff: noqa

from collections import defaultdict
import AST
from SymbolTable import SymbolTable

ttype = defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: "")))

for op in ["+", "-", "*", "/"]:
    ttype[op]["int"]["int"] = "int"
    ttype[op]["int"]["float"] = "float"
    ttype[op]["float"]["int"] = "float"
    ttype[op]["float"]["float"] = "float"
    ttype[op]["str"]["str"] = "str"
    ttype[op]["vector"]["vector"] = "vector"
ttype["*"]["str"]["int"] = "str"

for op in [">", "<", ">=", "<=", "==", "!="]:
    ttype[op]["int"]["int"] = "bool"
    ttype[op]["int"]["float"] = "bool"
    ttype[op]["float"]["int"] = "bool"
    ttype[op]["float"]["float"] = "bool"

for op in ["and", "or", "xor"]:
    ttype[op]["bool"]["bool"] = "bool"
ttype["not"]["bool"][""] = "bool"

for op in [".+", ".-", ".*", "./"]:
    ttype[op]["vector"]["vector"] = "vector"

for op in ["+=", "-=", "*=", "/="]:
    ttype[op]["int"]["int"] = "int"
    ttype[op]["int"]["float"] = "float"
    ttype[op]["float"]["int"] = "float"
    ttype[op]["float"]["float"] = "float"
    ttype[op]["vector"]["vector"] = "vector"
ttype["+="]["str"]["str"] = "str"
ttype["*="]["str"]["int"] = "str"


class NodeVisitor(object):
    def __init__(self):
        self.symbol_table = SymbolTable(None, "global")
        self.current_scope = self.symbol_table
        self.loop_indent = 0

    def visit(self, node):
        method = "visit_" + node.__class__.__name__
        visitor = getattr(self, method, self.generic_visit)
        return visitor(node)

    def generic_visit(self, node):  # Called if no explicit visitor function exists for a node.
        if isinstance(node, list):
            for elem in node:
                self.visit(elem)
        else:
            for child in node.children:
                if isinstance(child, list):
                    for item in child:
                        if isinstance(item, AST.Node):
                            self.visit(item)
                elif isinstance(child, AST.Node):
                    self.visit(child)


class TypeChecker(NodeVisitor):
    def print_error(self, lineno, msg):
        print(f"\033[91m[line {lineno}] {msg}\033[0m")

    def visit_InstrOrEmpty(self, node: AST.InstrOrEmpty):
        self.visit(node.instructions)

    def visit_Instructions(self, node: AST.Instructions):
        if node.instructions is None:
            return
        for instruction in node.instructions:
            self.visit(instruction)

    def visit_Id(self, node: AST.Id):
        return self.symbol_table.get(node.id)

    def visit_BinExpr(self, node: AST.BinExpr):
        node.v_type = "float"
        type_l = self.visit(node.left)
        type_r = self.visit(node.right)
        op = node.op
        if ttype[op][type_l][type_r] == "":
            self.print_error(node.lineno, f"Type error ({type_l} {op} {type_r})")
            return None

        if type_l == "vector" or type_r == "vector":
            was_l_tr = was_r_tr = False
            if isinstance(node.left, AST.Unary):
                if node.left.operation == "TRANSPOSE":
                    was_l_tr = True
                node.left = node.left.expr
            if isinstance(node.right, AST.Unary):
                if node.right.operation == "TRANSPOSE":
                    was_r_tr = True
                node.right = node.right.expr

            if isinstance(node.left, AST.Id):
                left_dims = self.symbol_table.get_v_dims(node.left.id)
                node.v_type = self.symbol_table.get_v_type(node.left.id)
            elif isinstance(node.left, AST.BinExpr):
                left_dims = node.left.dims
            elif isinstance(node.left, AST.Vector):
                left_dims = node.left.dims
            else:
                self.print_error(node.lineno, "Error in visit_BinExpr \nEXITING")
                print(node.left)
                exit()
            if was_l_tr:
                left_dims = left_dims[::-1]

            if isinstance(node.right, AST.Id):
                right_dims = self.symbol_table.get_v_dims(node.right.id)
                node.v_type = self.symbol_table.get_v_type(node.left.id)
            elif isinstance(node.right, AST.BinExpr):
                right_dims = node.right.dims
            elif isinstance(node.right, AST.Vector):
                right_dims = node.right.dims
            else:
                self.print_error(node.lineno, "Error in visit_BinExpr \nEXITING")
                print(node.left, node.right)
                exit()
            if was_r_tr:
                right_dims = right_dims[::-1]

            if len(right_dims) != len(left_dims):
                self.print_error(node.lineno, f"Vector dimensions do not match ({len(left_dims)} != {len(right_dims)})")
                return None

            for i in range(len(right_dims)):
                if isinstance(left_dims[i], AST.IntNum):
                    dim_l = left_dims[i].intnum
                else:
                    dim_l = left_dims[i]
                if isinstance(right_dims[i], AST.IntNum):
                    dim_r = right_dims[i].intnum
                else:
                    dim_r = right_dims[i]
                if dim_l != dim_r:
                    self.print_error(node.lineno, f"Vector dimensions do not match ({dim_l} != {dim_r})")
                    return None
            node.dims = left_dims
        return ttype[op][type_l][type_r]

    def visit_If(self, node: AST.If):
        self.symbol_table = self.symbol_table.pushScope("if")
        self.visit(node.cond)
        self.visit(node.if_body)
        self.symbol_table = self.symbol_table.popScope()
        if node.else_body is not None:
            self.symbol_table = self.symbol_table.pushScope("else")
            self.visit(node.else_body)
            self.symbol_table = self.symbol_table.popScope()

    def visit_Return(self, node: AST.Return):
        return self.visit(node.expr)

    def visit_Break(self, node: AST.Break):
        if self.loop_indent == 0:
            self.print_error(node.lineno, "Break outside of loop")

    def visit_Continue(self, node: AST.Continue):
        if self.loop_indent == 0:
            self.print_error(node.lineno, "Continue outside of loop")

    def visit_For(self, node: AST.For):
        self.symbol_table = self.symbol_table.pushScope("for")
        self.loop_indent += 1
        type_s = self.visit(node.cond_start)
        type_e = self.visit(node.cond_end)
        if type_s is None or type_e is None or type_s != type_e:
            self.print_error(node.lineno, f"For loop condition types do not match ({type_s} != {type_e})")
            self.symbol_table.put(node.id, None)
        else:
            if isinstance(node.id, AST.Id):
                self.symbol_table.put(node.id.id, type_s)
            else:
                self.symbol_table.put(node.id, type_s)
        self.visit(node.body)
        self.symbol_table = self.symbol_table.popScope()
        self.loop_indent -= 1

    def visit_While(self, node: AST.While):
        self.symbol_table = self.symbol_table.pushScope("while")
        self.loop_indent += 1
        self.visit(node.cond)
        self.visit(node.body)
        self.symbol_table = self.symbol_table.popScope()
        self.loop_indent -= 1

    def visit_AssignOp(self, node: AST.AssignOp):
        val_type = self.visit(node.right)
        if val_type is None:
            return None
        left_id = node.left.id
        if node.op == "=":
            if isinstance(left_id, str):
                self.symbol_table.put(left_id, val_type)
            else:
                self.symbol_table.put(left_id.id, val_type)
            if val_type == "vector":
                if isinstance(node.right, AST.Unary):
                    self.symbol_table.v_dims[left_id] = node.right.expr.dims[::-1]
                    self.symbol_table.v_type[left_id] = node.right.expr.v_type
                elif isinstance(node.right.dims, AST.IntNum):
                    self.symbol_table.v_dims[left_id] = node.right.dims.intnum
                    self.symbol_table.v_type[left_id] = node.right.v_type
                else:
                    self.symbol_table.v_dims[left_id] = node.right.dims
                    self.symbol_table.v_type[left_id] = node.right.v_type
        else:
            var_type = self.symbol_table.get(left_id)
            if var_type == "vector" and val_type == "vector":
                var_d = self.symbol_table.v_dims[left_id]
                val_d = node.right.dims
                if len(var_d) != len(val_d):
                    self.print_error(node.lineno, f"Vector dimensions do not match ({len(var_d)} != {len(val_d)})")
                    return None
                for i in range(len(var_d)):
                    if var_d[i] != val_d[i]:
                        self.print_error(node.lineno, f"Vector dimensions do not match ({var_d[i]} != {val_d[i]})")
                        return None
            if ttype[node.op][var_type][val_type] != "":
                return ttype[node.op][var_type][val_type]
            else:
                self.print_error(node.lineno, f"Type error ({var_type} {node.op} {val_type})")
                return None

    def visit_Vector(self, node: AST.Vector):
        if isinstance(node.vector[0], AST.Vector):
            dim = node.vector[0].dims
        elif isinstance(node.vector[0], list):
            dim = [len(node.vector[0])]
        else:
            dim = [1]
        for element in node.vector:
            if isinstance(element, AST.Vector):
                self.visit(element)
                dim_e = element.dims
            elif isinstance(element, list):
                dim_e = [len(element)]
            else:
                dim_e = [1]
            for i in range(len(dim)):
                if dim[i] != dim_e[i]:
                    self.print_error(node.lineno, f"Vector dimensions do not match ({dim[i]} != {dim_e[i]})")
                    return None
        return "vector"

    def visit_Print(self, node: AST.Print):
        for i in node.printargs:
            self.visit(i)

    def visit_String(self, node: AST.String):
        return "str"

    def visit_IntNum(self, node: AST.IntNum):
        return "int"

    def visit_FloatNum(self, node: AST.FloatNum):
        return "float"

    def visit_Variable(self, node: AST.Variable):
        if node.id.id not in self.symbol_table.v_dims:
            self.print_error(node.lineno, f"Variable {node.id.id} not defined")
            return None
        dims = self.symbol_table.v_dims[node.id.id]
        if len(dims) != len(node.index):
            self.print_error(node.lineno, f"Vector dimensions do not match ({len(dims)} != {len(node.index)})")
            return None
        for i in range(len(node.index)):
            if isinstance(node.index[i], tuple):
                if self.visit(node.index[i][0]) != "int" or self.visit(node.index[i][1]) != "int":
                    self.print_error(node.lineno, "Vector index must be int")
                    return None
                if node.index[i][0].intnum >= dims[i].intnum or node.index[i][1].intnum >= dims[i].intnum:
                    self.print_error(node.lineno, "Index out of bounds")
                    return None
                if node.index[i][0].intnum >= node.index[i][1].intnum:
                    self.print_error(node.lineno, "Invalid range")
                    return None
            else:
                if self.visit(node.index[i]) != "int":
                    self.print_error(node.lineno, "Vector index must be int")
                    return None
                if node.index[i].intnum >= dims[i].intnum:
                    self.print_error(node.lineno, "Index out of bounds")
                    return None
        return self.symbol_table.v_type[node.id.id]

    def visit_Unary(self, node: AST.Unary):
        if node.operation == "TRANSPOSE":
            if isinstance(node.expr, AST.Id):
                self.symbol_table.v_dims[node.expr.id] = self.symbol_table.v_dims[node.expr.id][::-1]
        return self.visit(node.expr)

    def visit_MatrixFunc(self, node: AST.MatrixFunc):
        for el in node.dims:
            if self.visit(el) != "int":
                self.print_error(node.lineno, "Matrix function argument must be int")
                return None
        return "vector"
