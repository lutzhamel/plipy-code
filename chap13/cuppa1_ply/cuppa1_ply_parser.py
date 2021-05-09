# YACC parser for Cuppa1

from ply import yacc
from cuppa1_ply_lex import tokens, lexer

# set precedence and associativity
# NOTE: all arithmetic operator need to have tokens
#       so that we can put them into the precedence table
precedence = (
              ('left', 'EQ', 'LE'),
              ('left', 'PLUS', 'MINUS'),
              ('left', 'MUL', 'DIV'),
              ('right', 'UMINUS', 'NOT')
             )


def p_grammar(_):
    '''
    program : stmt_list

    stmt_list : stmt_list stmt
              |

    stmt : ID '=' exp opt_semi
         | GET ID opt_semi
         | PUT exp opt_semi
         | WHILE '(' exp ')' stmt
         | IF '(' exp ')' stmt
         | IF '(' exp ')' stmt ELSE stmt
         | '{' stmt_list '}'

    opt_semi : ';'
             |

    exp : exp PLUS exp
        | exp MINUS exp
        | exp MUL exp
        | exp DIV exp
        | exp EQ exp
        | exp LE exp
        | INTEGER
        | ID
        | '(' exp ')'
        | MINUS exp %prec UMINUS
        | NOT exp
    '''
    pass

def p_error(t):
    raise SyntaxError("syntax error at '{}'".format(t.value))

### build the parser
parser = yacc.yacc()

if __name__ == "__main__":
    from sys import stdin
    char_stream = stdin.read()
    parser.parse(char_stream)
    print("parse successful.")
