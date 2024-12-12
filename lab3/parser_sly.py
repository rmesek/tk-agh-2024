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
        ("nonassoc", "'"),
    )

    @_("statements stmt", "stmt")
    def statements(self, p):
        if len(p) == 1:
            return AST.StatementsNode(statements=[p[0]], lineno=p.lineno)

        statements = p[0].statements.copy()
        statements.append(p[1])

        return AST.StatementsNode(statements=statements, lineno=p.lineno)

    @_(
        '";"',
        '"{" statements "}"',
        "if_stmt",
        "while_stmt",
        "for_stmt",
        "assign_expr",
        "print_stmt",
        'BREAK ";"',
        'CONTINUE ";"',
        'RETURN expr ";"',
    )
    def stmt(self, p):
        try:
            if p.BREAK is not None:
                return AST.BreakStatement(lineno=p.lineno)
        except AttributeError:
            pass
        try:
            if p.CONTINUE is not None:
                return AST.ContinueStatement(lineno=p.lineno)
        except AttributeError:
            pass
        try:
            if p.RETURN is not None:
                return AST.ReturnStatement(expr=p[1], lineno=p.lineno)
        except AttributeError:
            pass

        if p[0] == ";":
            return AST.BlankStatement(lineno=p.lineno)

        if len(p) == 1:
            return p[0]

        return p[1]

    @_(
        'IF "(" relation_expr ")" stmt ELSE stmt',
        'IF "(" relation_expr ")" stmt %prec IFX',
    )
    def if_stmt(self, p):
        else_body = None

        try:
            if p.ELSE is not None:
                else_body = p[6]
        except AttributeError:
            pass

        return AST.IfElseNode(condition=p[2], if_body=p[4], else_body=else_body, lineno=p.lineno)

    @_('WHILE "(" relation_expr ")" stmt')
    def while_stmt(self, p):
        return AST.WhileNode(condition=p.relation_expr, body=p.stmt, lineno=p.lineno)

    @_('FOR ID "=" id_int ":" id_int stmt')
    def for_stmt(self, p):
        return AST.ForNode(variable=p.ID, start=p.id_int0, end=p.id_int1, body=p.stmt, lineno=p.lineno)

    @_("ID", "INTNUM")
    def id_int(self, p):
        try:
            if p.INTNUM is not None:
                return AST.IntNum(value=p[0], lineno=p.lineno)
        except AttributeError:
            pass
        try:
            if p.ID is not None:
                return AST.IDNode(name=p[0], lineno=p.lineno)
        except AttributeError:
            pass

    @_('PRINT print_rek ";"')
    def print_stmt(self, p):
        return AST.PrintNode(value=p[1], lineno=p.lineno)

    @_('print_rek "," expr', "expr")
    def print_rek(self, p):
        if len(p) == 3:
            values = p.print_rek.values + [p.expr]
        else:
            values = [p.expr]

        return AST.PrintRekNode(values=values, lineno=p.lineno)

    @_("INTNUM", "FLOAT", "ID", "STRING")
    def value(self, p):
        try:
            if p.INTNUM is not None:
                return AST.IntNum(value=p[0], lineno=p.lineno)
        except AttributeError:
            pass
        try:
            if p.FLOAT is not None:
                return AST.FloatNum(value=p[0], lineno=p.lineno)
        except AttributeError:
            pass
        try:
            if p.ID is not None:
                return AST.IDNode(name=p[0], lineno=p.lineno)
        except AttributeError:
            pass
        try:
            if p.STRING is not None:
                return AST.Variable(name=p[0], lineno=p.lineno)
        except AttributeError:
            pass

        return None

    @_(
        "value",
        "assign_expr",
        "relation_expr",
        "matrix_funcs",
        "matrix_ref",
        "SUB expr",
        '"[" matrix_rows "]"',
        '"[" string_of_num "]"',
        'expr "\'"',
        '"(" expr ")"',
    )
    def expr(self, p):
        if len(p) == 1:
            return AST.ExpressionNode(expr=p[0], lineno=p.lineno)

        try:
            if p.SUB is not None:
                return AST.NegationNode(expr=p[1], lineno=p.lineno)
        except AttributeError:
            pass

        if p[1] == "'":
            return AST.TransposeNode(expr=p[0], lineno=p.lineno)

        if p[0] == "(":
            return AST.ExpressionNode(expr=p[1], lineno=p.lineno)

        return AST.MatrixNode(values=p[1], lineno=p.lineno)

    @_("expr ADD expr", "expr SUB expr", "expr MUL expr", "expr DIV expr")
    def expr(self, p):
        return AST.BinExpr(op=p[1], left=p[0], right=p[2], lineno=p.lineno)

    @_("expr DOTADD expr", "expr DOTSUB expr", "expr DOTMUL expr", "expr DOTDIV expr")
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

    @_("ID", "matrix_ref")
    def id_ref(self, p):
        try:
            if p.matrix_ref is not None:
                return p[0]
        except AttributeError:
            pass

        return AST.IDRefNode(value=p[0], lineno=p.lineno)

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

    @_('ZEROS "(" INTNUM ")"', 'ONES "(" INTNUM ")"', 'EYE "(" INTNUM ")"')
    def matrix_funcs(self, p):
        func_name = p[0]

        if func_name == "zeros":
            return AST.ZerosNode(func_name=p[0], arg=p[2], lineno=p.lineno)
        elif func_name == "ones":
            return AST.OnesNode(func_name=p[0], arg=p[2], lineno=p.lineno)
        elif func_name == "eye":
            return AST.EyeNode(func_name=p[0], arg=p[2], lineno=p.lineno)

    @_('ID "[" string_of_num "]"')
    def matrix_ref(self, p):
        return AST.MatrixRefNode(id=p[0], values=p[2], lineno=p.lineno)

    @_('"[" string_of_num "]"', 'matrix_rows "," "[" string_of_num "]"')
    def matrix_rows(self, p):
        if len(p) == 3:
            return AST.MatrixRowsNode(values=[p[1]], lineno=p.lineno)

        rows = p.matrix_rows.values.copy()
        rows.append(p[3])

        return AST.MatrixRowsNode(values=rows, lineno=p.lineno)

    @_("INTNUM", 'string_of_num "," INTNUM')
    def string_of_num(self, p):
        if len(p) == 1:
            return AST.StringOfNumNode(values=[p[0]], lineno=p.lineno)
        else:
            values = p[0].values.copy()
            values.append(p[2])
            return AST.StringOfNumNode(values=values, lineno=p.lineno)

    # Error handling
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
