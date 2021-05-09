# YACC parser, pattern language

from ply import yacc
from pattern_ply_lex import tokens, lexer

def p_grammar(p):
    '''
    stmtlist : stmtlist stmt
             |

    stmt : pattern '=' exp
         | exp

    exp : ID
        | '(' ')'
        | '(' exp ')'

    pattern : ID
            | '(' ')'
            | '(' pattern ')'
    '''
    pass

def p_error(t):
    raise SyntaxError("syntax error at '{}'".format(t.value))

### build the parser
parser = yacc.yacc()

if __name__ == "__main__":
    from sys import stdin
    char_stream = stdin.read()
    try:
        parser.parse(char_stream)
        print("parse successful.")
    except Exception as e:
        print("error: " + str(e))
