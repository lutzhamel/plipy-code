# YACC specification for exp grammar

from ply import yacc
from exp_ply_lex import tokens, lexer

precedence = (
              ('left', 'PLUS'),
             )

def p_start(p):
    "start : exp"
    pass

def p_plus_exp(p):
    "exp : exp PLUS exp"
    pass

def p_id_exp(p):
    "exp : ID"
    pass

def p_error(t):
    raise SyntaxError("syntax error at '{}'".format(t.value))

# build the parser
parser = yacc.yacc()

# run the parser from the command line
if __name__ == "__main__":
    from sys import stdin
    char_stream = stdin.read()
    try:
        parser.parse(char_stream,lexer=lexer)
        print("parse successful.")
    except Exception as e:
        print("error: " + str(e))
