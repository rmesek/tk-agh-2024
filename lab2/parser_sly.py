# type: ignore
# ruff: noqa

from sly import Parser
from scanner_sly import Scanner


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
        pass

    # Optional list of instructions
    @_('instructions_opt instruction')
    def instructions_opt(self, p):
        pass

    @_('')
    def instructions_opt(self, p):
        pass

    # List of instructions
    @_('instructions instruction')
    def instructions(self, p):
        pass

    @_('instruction')
    def instructions(self, p):
        pass

    # Definitions of different types of instructions
    @_('";"',
       '"{" instructions "}"',
       'if_statement',
       'while_statement',
       'for_statement',
       'assignment',
       'print_statement',
       'BREAK ";"',
       'CONTINUE ";"',
       'RETURN expression ";"')
    def instruction(self, p):
        pass

    # If statement with optional else
    @_('IF "(" condition ")" instruction ELSE instruction',
       'IF "(" condition ")" instruction %prec IFX')
    def if_statement(self, p):
        pass

    # While loop
    @_('WHILE "(" condition ")" instruction')
    def while_statement(self, p):
        pass

    # For loop
    @_('FOR ID "=" range ":" range instruction')
    def for_statement(self, p):
        pass

    # Range in for loop
    @_('ID',
       'INTNUM')
    def range(self, p):
        pass

    # Print statement
    @_('PRINT print_list ";"')
    def print_statement(self, p):
        pass

    # List of expressions to print
    @_('print_list "," expression',
       'expression')
    def print_list(self, p):
        pass

    # Types of expressions
    @_('INTNUM',
       'FLOATNUM',
       'ID',
       'STRING',
       'assignment',
       'condition',
       'matrix_function',
       'matrix_access',
       '"-" expression',
       '"[" matrix_rows "]"',
       'expression "\'"',
       '"(" expression ")"')
    def expression(self, p):
        pass

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
        pass

    # Assignment operations
    @_('variable "=" expression ";"',
       'variable ADDASSIGN expression ";"',
       'variable SUBASSIGN expression ";"',
       'variable MULASSIGN expression ";"',
       'variable DIVASSIGN expression ";"')
    def assignment(self, p):
        pass

    # Variable or matrix access
    @_('ID',
       'matrix_access')
    def variable(self, p):
        pass

    # Conditional expressions
    @_('expression "<" expression',
       'expression ">" expression',
       'expression LE expression',
       'expression GE expression',
       'expression EQ expression',
       'expression NE expression')
    def condition(self, p):
        pass

    # Matrix functions like zeros, ones, eye
    @_('ZEROS "(" INTNUM ")"',
       'ONES "(" INTNUM ")"',
       'EYE "(" INTNUM ")"')
    def matrix_function(self, p):
        pass

    # Accessing elements of a matrix with indices
    @_('ID "[" index_list "]"')
    def matrix_access(self, p):
        pass

    @_('index_list "," index',
       'index')
    def index_list(self, p):
        pass

    @_('ID',
       'INTNUM')
    def index(self, p):
        pass

    @_('matrix_rows "," matrix_row',
       'matrix_row')
    def matrix_rows(self, p):
        pass

    @_('"[" number_list "]"')
    def matrix_row(self, p):
        pass

    # List of numbers with optional unary minus
    @_('number_list "," signed_number',
       'signed_number')
    def number_list(self, p):
        pass

    # Signed numbers (optional unary minus)
    @_('number',
       '"-" number')
    def signed_number(self, p):
        pass

    @_('FLOATNUM',
       'INTNUM')
    def number(self, p):
        pass

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
        r"example_full.txt",
        r"example1.m",
        r"example2.m",
        r"example3.m",
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