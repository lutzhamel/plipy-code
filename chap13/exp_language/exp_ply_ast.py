# YACC specification for the exp grammar with AST generation

from ply import yacc
from exp_ply_lex import tokens, lexer
from dumpast import dumpast

precedence = (
              ('left', 'PLUS'),
             )

def p_start(p):
    "start : exp"
    dumpast(p[1])

def p_plus_exp(p):
    "exp : exp PLUS exp"
    p[0] = ('PLUS', p[1], p[3])

def p_id_exp(p):
    "exp : ID"
    p[0] = ('ID', p[1])

def p_error(t):
    raise SyntaxError("syntax error at '{}'"
                .format(t.value))

# build the parser
parser = yacc.yacc()

# run the parser from the command line
if __name__ == "__main__":
    from sys import stdin
    char_stream = stdin.read()
    try:
        parser.parse(char_stream, lexer=lexer)
    except Exception as e:
        print("error: " + str(e))
