# type: ignore
# ruff: noqa

import sys
from sly import Lexer


class Scanner(Lexer):
    def __init__(self):
        self.nesting_level = 0

    ignore = r" \t"
    ignore_comment = r"#.*"

    tokens = {
        DOTADD, DOTSUB, DOTMUL, DOTDIV, ADDASSIGN, SUBASSIGN, MULASSIGN,
        DIVASSIGN, ADD, SUB, MUL, DIV, LT, GT, LTE, GTE, NEQ, EQ, ID,
        INTNUM, FLOAT, STRING,
        # reserved tokens
        IF, ELSE, FOR, WHILE, BREAK, CONTINUE, RETURN, EYE, ZEROS, ONES, 
        PRINT,   
        }
    
    literals = {"(", ")", "{", "}", "[", "]", ",", ";", ":", "'", "="}

    EQ = r"=="; NEQ = r"!="
    LTE = r"<="; GTE = r">="
    LT = r"<"; GT = r">"

    ADDASSIGN = r"\+="; SUBASSIGN = r"-="
    MULASSIGN = r"\*="; DIVASSIGN = r"/="

    ADD = r"\+"; SUB = r"-"
    MUL = r"\*"; DIV = r"/"

    DOTADD = r"\.\+"; DOTSUB = r"\.-"
    DOTMUL = r"\.\*"; DOTDIV = r"\./"


    STRING = r"\".*\""
    ID = r"[a-zA-Z_][\w_]*"
    ID["if"] = IF
    ID["else"] = ELSE
    ID["while"] = WHILE
    ID["for"] = FOR
    ID["break"] = BREAK
    ID["continue"] = CONTINUE
    ID["return"] = RETURN
    ID["eye"] = EYE
    ID["zeros"] = ZEROS
    ID["ones"] = ONES
    ID["print"] = PRINT

    @_(r"[\{\[\(]")
    def lbrace(self, t):
        t.type = t.value
        self.nesting_level += 1
        return t

    @_(r"[\}\]\)]")
    def rbrace(self, t):
        t.type = t.value
        self.nesting_level -= 1
        return t

    @_(r"\d+[eE][-+]?\d+|\d*\.(\d*([eE][-+]?\d+)?)?")
    def FLOAT(self, t):
        t.value = float(t.value)
        return t

    @_(r"\d+")
    def INTNUM(self, t):
        t.value = int(t.value)
        return t

    @_(r"\n+")
    def ignore_newline(self, t):
        self.lineno += len(t.value)

    def error(self, t):
        print(f"{"\033[91m"}Illegal character '{t.value[0]}'"
              + f" at line {t.lineno}!{"\033[0m"}")
        self.index += 1

    @_(r"[\d\.\?]+[a-zA-Z]*")
    def bad_token(self, t):
        print(f"ERROR: Unknown token at line {self.lineno}: {t.value}")


if __name__ == "__main__":
    try:
        filename = sys.argv[1] if len(sys.argv) > 1 else "example.txt"
        file = open(filename, "r")
    except IOError:
        print("Cannot open {0} file".format(filename))
        sys.exit(0)

    text = file.read()
    lexer = Scanner()

    for tok in lexer.tokenize(text):
        print(f"({tok.lineno}): {tok.type}({tok.value})")
