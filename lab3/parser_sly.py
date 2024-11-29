# type: ignore
# ruff: noqa

from sly import Parser
from scanner_sly import Scanner
import AST


class Mparser(Parser):
    tokens = Scanner.tokens

    debugfile = "parser.out"

    # Operator precedence and associativity
    precedence = (
        ("nonassoc",    "IFX"),
        ("nonassoc",    "ELSE"),
        ("nonassoc",    "LE", "GE", "EQ", "NE", "<", ">"),
        ("left",        "+", "-", "DOTADD", "DOTSUB"),
        ("left",        "*", "/", "DOTMUL", "DOTDIV"),
        ("nonassoc",    "'")
    )

    # Starting rule
    @_('instructions_opt')
    def program(self, p):
        return p.instructions_opt

    # Optional list of instructions
    @_('instructions_opt instruction')
    def instructions_opt(self, p):
        return [*p.instructions_opt, p.instruction] if p.instructions_opt else [p.instruction]

    @_('')
    def instructions_opt(self, p):
        return []

    # List of instructions
    @_('instructions instruction')
    def instructions(self, p):
        return [*p.instructions, p.instruction]

    @_('instruction')
    def instructions(self, p):
        return [p.instruction]

    # Types of expressions
    @_('INTNUM')
    def expression(self, p):
        return AST.IntNum(p.INTNUM)

    @_('FLOATNUM')
    def expression(self, p):
        return AST.FloatNum(p.FLOATNUM)

    @_('ID')
    def expression(self, p):
        return AST.Variable(p.ID)

    @_('STRING')
    def expression(self, p):
        return AST.String(p.STRING)

    @_('"-" expression')
    def expression(self, p):
        return AST.UnaryExpr('-', p.expression)

    @_('expression "\'"')
    def expression(self, p):
        return AST.Transpose(p.expression)

    @_('"(" expression ")"')
    def expression(self, p):
        return p.expression

    # Binary expressions
    @_('expression "+" expression',
    'expression "-" expression',
    'expression "*" expression', 
    'expression "/" expression',
    'expression DOTADD expression',
    'expression DOTSUB expression',
    'expression DOTMUL expression',
    'expression DOTDIV expression')
    def expression(self, p):
        return AST.BinExpr(p[1], p[0], p[2])

    # Assignment operations
    @_('variable "=" expression ";"',
    'variable ADDASSIGN expression ";"',
    'variable SUBASSIGN expression ";"',
    'variable MULASSIGN expression ";"',
    'variable DIVASSIGN expression ";"')
    def assignment(self, p):
        return AST.Assignment(p[1], p.variable, p.expression)

    # Variable or matrix access
    @_('ID')
    def variable(self, p):
        return AST.Variable(p.ID)

    @_('matrix_access')
    def variable(self, p):
        return p.matrix_access

    # Conditional expressions  
    @_('expression "<" expression',
    'expression ">" expression',
    'expression LE expression',
    'expression GE expression',
    'expression EQ expression',
    'expression NE expression')
    def condition(self, p):
        return AST.Condition(p[1], p[0], p[2])

    # Matrix functions
    @_('ZEROS "(" INTNUM ")"',
    'ONES "(" INTNUM ")"',
    'EYE "(" INTNUM ")"')
    def matrix_function(self, p):
        return AST.MatrixFunction(p[0], AST.IntNum(p.INTNUM))

    # Matrix access
    @_('ID "[" index_list "]"')
    def matrix_access(self, p):
        return AST.MatrixAccess(AST.Variable(p.ID), p.index_list)

    @_('index_list "," index')
    def index_list(self, p):
        return [*p.index_list, p.index]

    @_('index')
    def index_list(self, p):
        return [p.index]

    @_('ID')
    def index(self, p):
        return AST.Variable(p.ID)

    @_('INTNUM')
    def index(self, p):
        return AST.IntNum(p.INTNUM)

    # Matrix construction
    @_('matrix_rows "," matrix_row')
    def matrix_rows(self, p):
        return [*p.matrix_rows, p.matrix_row]

    @_('matrix_row')
    def matrix_rows(self, p):
        return [p.matrix_row]

    @_('"[" number_list "]"')
    def matrix_row(self, p):
        return p.number_list

    @_('number_list "," signed_number')
    def number_list(self, p):
        return [*p.number_list, p.signed_number]

    @_('signed_number')
    def number_list(self, p):
        return [p.signed_number]

    @_('number')
    def signed_number(self, p):
        return p.number

    @_('"-" number') 
    def signed_number(self, p):
        return AST.UnaryExpr('-', p.number)

    @_('FLOATNUM')
    def number(self, p):
        return AST.FloatNum(p.FLOATNUM)

    @_('INTNUM')
    def number(self, p):
        return AST.IntNum(p.INTNUM)
    
    # Error handling
    def error(self, p):
        if p:
            print(f"\033[91mSyntax error at '{p.value}'"
                  + f" in line {p.lineno}!\033[0m")
            self.restart()
        else:
            print("\033[91mSyntax error at EOF\033[0m")

if __name__ == '__main__':
    from scanner_sly import Scanner

    FILENAMES = [
        r"example.txt",
        r"lab2/example1.m",
        r"lab2/example2.m",
        r"lab2/example3.m",
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

        result = parser.parse(lexer.tokenize(text))
        print(f"\033[92m{filename} parsed successfully!\033[0m")