# type: ignore
# ruff: noqa

import sys
from sly import Lexer


class Scanner(Lexer):
    # operatory binare: +, -, *, /
    # macierzowe operatory binarne 
    #   (dla operacji element po elemencie): .+, .-, .*, ./
    # operatory przypisania: =, +=, -=, *=, /=
    # operatory relacyjne: <, >, <=, >=, !=, ==
    # nawiasy: (,), [,], {,}
    # operator zakresu: :
    # transpozycja macierzy: '
    # przecinek i średnik: , ;
    # słowa kluczowe: if, else, for, while
    # słowa kluczowe: break, continue oraz return
    # słowa kluczowe: eye, zeros oraz ones
    # słowa kluczowe: print
    # identyfikatory (pierwszy znak identyfikatora to litera lub 
    #   znak _, w kolejnych znakach mogą dodatkowo wystąpić cyfry)
    # liczby całkowite
    # liczby zmiennoprzecinkowe
    # stringi

    # String containing ignored characters between tokens
    # białe znaki: spacje, tabulatory, znaki nowej linii
    # komentarze: komentarze rozpoczynające się znakiem # 
    #   do znaku końca linii
    ignore = " \t"

    ignore_comment = r"#.*"

    # Set of token names.
    tokens = {
        DOTADD, DOTSUB, DOTMUL, DOTDIV, ADDASSIGN, SUBASSIGN, MULASSIGN, 
        DIVASSIGN, LE, GE, NE, EQ, ID, INTNUM, FLOATNUM, STRING,
        # reserved tokens
        IF, ELSE, FOR, WHILE, BREAK, CONTINUE, RETURN, EYE, ZEROS, ONES,
        PRINT,
    }

    literals = {
        "<", ">", "=", "+", "-", "*", "/", "{", "}", "[", "]", "(", ")",
        ":", "'", ",", ";",
    }

    EQ = r"=="; NE = r"!="
    LE = r"<="; GE = r">="
    ADDASSIGN = r"\+="; SUBASSIGN = r"-="
    MULASSIGN = r"\*="; DIVASSIGN = r"/="
    DOTADD = r"\.\+"; DOTSUB = r"\.-"
    DOTMUL = r"\.\*"; DOTDIV = r"\./"

    ID = r"[a-zA-Z_][a-zA-Z0-9_]*"
    ID["if"] = IF
    ID["else"] = ELSE
    ID["for"] = FOR
    ID["while"] = WHILE
    ID["break"] = BREAK
    ID["continue"] = CONTINUE
    ID["return"] = RETURN
    ID["eye"] = EYE
    ID["zeros"] = ZEROS
    ID["ones"] = ONES
    ID["print"] = PRINT

    @_(r"\d+[eE][-+]?\d+|\d*\.(\d*([eE][-+]?\d+)?)?")
    def FLOATNUM(self, t):
        return t

    @_(r"\d+")
    def INTNUM(self, t):
        return t

    @_(r"\".*?\"")
    def STRING(self, t):
        t.value = t.value[1:-1]
        return t

    @_(r"\n+")
    def ignore_newline(self, t):
        self.lineno += len(t.value)

    def error(self, t):
        print(f"{"\033[91m"}Illegal character '{t.value[0]}'"
              + f" at line {t.lineno}!{"\033[0m"}")
        self.index += 1


if __name__ == "__main__":
    try:
        filename = sys.argv[1] if len(sys.argv) > 1 \
                               else "example.txt"
        file = open(filename, "r")
    except IOError:
        print("Cannot open {0} file".format(filename))
        sys.exit(0)

    text = file.read()
    lexer = Scanner()

    for tok in lexer.tokenize(text):
        print(f"({tok.lineno}): {tok.type}({tok.value})")
