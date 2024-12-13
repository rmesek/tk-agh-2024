# type: ignore
# ruff: noqa

from sly import Parser
from scanner_sly import Scanner
import AST
from TreePrinter import TreePrinter


class Mparser(Parser):
    tokens = Scanner.tokens

    debugfile = "parser.out"

    precedence = (
        ("nonassoc", IFX),
        ("nonassoc", ELSE),
        ("nonassoc", LTE, GTE, EQ, NEQ, LT, GT),
        ("left", ADD, SUB, DOTADD, DOTSUB),
        ("left", MUL, DIV, DOTMUL, DOTDIV),
        ("right", UMINUS),
        ("nonassoc", "'"),
    )

    @_("statements stmt")
    def statements(self, p):
        return AST.StatementsNode(statements=p[0].statements + [p[1]], lineno=p.lineno)

    @_("stmt")
    def statements(self, p):
        return AST.StatementsNode(statements=[p[0]], lineno=p.lineno)

    @_('";"')
    def stmt(self, p):
        return AST.BlankStatement(lineno=p.lineno)

    @_('"{" statements "}"')
    def stmt(self, p):
        return p[1]

    @_('BREAK ";"')
    def stmt(self, p):
        return AST.BreakStatement(lineno=p.lineno)

    @_('CONTINUE ";"')
    def stmt(self, p):
        return AST.ContinueStatement(lineno=p.lineno)

    @_('RETURN expr ";"')
    def stmt(self, p):
        return AST.ReturnStatement(expr=p[1], lineno=p.lineno)

    @_(
        "if_stmt",
        "while_stmt",
        "for_stmt",
        "assign_expr",
        "print_stmt",
    )
    def stmt(self, p):
        return p[0]

    @_('IF "(" relation_expr ")" stmt ELSE stmt')
    def if_stmt(self, p):
        return AST.IfElseNode(condition=p[2], if_body=p[4], else_body=p[6], lineno=p.lineno)

    @_('IF "(" relation_expr ")" stmt %prec IFX')
    def if_stmt(self, p):
        return AST.IfElseNode(condition=p[2], if_body=p[4], else_body=None, lineno=p.lineno)

    @_('WHILE "(" relation_expr ")" stmt')
    def while_stmt(self, p):
        return AST.WhileNode(condition=p[2], body=p[4], lineno=p.lineno)

    @_('FOR ID "=" id_int ":" id_int stmt')
    def for_stmt(self, p):
        return AST.ForNode(variable=p[1], start=p[3], end=p[5], body=p[6], lineno=p.lineno)

    @_("ID")
    def id_int(self, p):
        return AST.IDNode(name=p[0], lineno=p.lineno)

    @_("INTNUM")
    def id_int(self, p):
        return AST.IntNum(value=p[0], lineno=p.lineno)

    @_("PRINT print_rek ';'")
    def print_stmt(self, p):
        return AST.PrintNode(value=p[1], lineno=p.lineno)

    @_("print_rek ',' expr")
    def print_rek(self, p):
        return AST.PrintRekNode(values=p[0].values + [p[2]], lineno=p.lineno)

    @_("expr")
    def print_rek(self, p):
        return AST.PrintRekNode(values=[p[0]], lineno=p.lineno)

    @_("INTNUM")
    def value(self, p):
        return AST.IntNum(value=p[0], lineno=p.lineno)

    @_("FLOAT")
    def value(self, p):
        return AST.FloatNum(value=p[0], lineno=p.lineno)

    @_("ID")
    def value(self, p):
        return AST.IDNode(name=p[0], lineno=p.lineno)

    @_("STRING")
    def value(self, p):
        return AST.Variable(name=p[0], lineno=p.lineno)
    
    @_(
        "value",
        "assign_expr",
        "relation_expr",
        "matrix_funcs",
        "matrix_ref",
    )
    def expr(self, p):
        return AST.ExpressionNode(expr=p[0], lineno=p.lineno)

    @_("SUB expr %prec UMINUS")
    def expr(self, p):
        return AST.NegationNode(expr=p[1], lineno=p.lineno)

    @_('expr "\'"')
    def expr(self, p):
        return AST.TransposeNode(expr=p[0], lineno=p.lineno)

    @_('"(" expr ")"')
    def expr(self, p):
        return AST.ExpressionNode(expr=p[1], lineno=p.lineno)

    @_(
        '"[" matrix_rows "]"',
        '"[" string_of_num "]"',
    )
    def expr(self, p):
        return AST.MatrixNode(values=p[1], lineno=p.lineno)

    @_(
        "expr ADD expr",
        "expr SUB expr",
        "expr MUL expr",
        "expr DIV expr",
        "expr DOTADD expr",
        "expr DOTSUB expr",
        "expr DOTMUL expr",
        "expr DOTDIV expr",
    )
    def expr(self, p):
        return AST.BinExpr(op=p[1], left=p[0], right=p[2], lineno=p.lineno)

    @_(
        'id_ref "=" expr ";"',
        'id_ref ADDASSIGN expr ";"',
        'id_ref SUBASSIGN expr ";"',
        'id_ref MULASSIGN expr ";"',
        'id_ref DIVASSIGN expr ";"',
    )
    def assign_expr(self, p):
        return AST.AssignExpression(left=p[0], operator=p[1], right=p[2], lineno=p.lineno)

    @_("ID")
    def id_ref(self, p):
        return AST.IDRefNode(value=p[0], lineno=p.lineno)

    @_("matrix_ref")
    def id_ref(self, p):
        return p[0]

    @_(
        "expr LT expr",
        "expr GT expr",
        "expr LTE expr",
        "expr GTE expr",
        "expr EQ expr",
        "expr NEQ expr",
    )
    def relation_expr(self, p):
        return AST.RelationExpression(op=p[1], left=p[0], right=p[2], lineno=p.lineno)

    @_('ZEROS "(" INTNUM ")"')
    def matrix_funcs(self, p):
        return AST.ZerosNode(func_name=p[0], arg=p[2], lineno=p.lineno)

    @_('ONES "(" INTNUM ")"')
    def matrix_funcs(self, p):
        return AST.OnesNode(func_name=p[0], arg=p[2], lineno=p.lineno)

    @_('EYE "(" INTNUM ")"')
    def matrix_funcs(self, p):
        return AST.EyeNode(func_name=p[0], arg=p[2], lineno=p.lineno)

    @_('ID "[" string_of_num "]"')
    def matrix_ref(self, p):
        return AST.MatrixRefNode(id=p[0], values=p[2], lineno=p.lineno)

    @_('"[" string_of_num "]"')
    def matrix_rows(self, p):
        return AST.MatrixRowsNode(values=[p[1]], lineno=p.lineno)

    @_('matrix_rows "," "[" string_of_num "]"')
    def matrix_rows(self, p):
        return AST.MatrixRowsNode(values=p[0].values + [p[3]], lineno=p.lineno)

    @_("INTNUM")
    def string_of_num(self, p):
        return AST.StringOfNumNode(values=[p[0]], lineno=p.lineno)

    @_("string_of_num ',' INTNUM")
    def string_of_num(self, p):
        return AST.StringOfNumNode(values=p[0].values + [p[2]], lineno=p.lineno)

    def error(self, p):
        if p:
            print(f"\033[91mSyntax error at '{p.value}' in line {p.lineno}!\033[0m")
            self.restart()
        else:
            print("\033[91mSyntax error at EOF\033[0m")


if __name__ == "__main__":
    from scanner_sly import Scanner

    FILENAMES = [
        r"lab2/example1.m",
        r"lab2/example2.m",
        r"lab2/example3.m",
        r"lab3/example.m",
        r"lab3/example1.m",
        r"lab3/example2.m",
        r"lab3/example3.m",
    ]

    lexer = Scanner()
    parser = Mparser()

    for filename in FILENAMES:
        try:
            file = open(filename, "r")
        except IOError:
            print(f"Cannot open {filename} file")
            continue

        text = file.read()

        ast = parser.parse(lexer.tokenize(text))
        ast.printTree()
        print(f"\033[92m{filename} parsed successfully!\033[0m")
