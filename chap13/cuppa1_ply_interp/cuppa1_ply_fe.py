# YACC frontend for Cuppa1

from ply import yacc
from cuppa1_ply_lex import tokens, lexer
from cuppa1_state import state

# set precedence and associativity
# NOTE: all arithmetic operator need to have tokens
#       so that we can put them into the precedence table
precedence = (
              ('left', 'EQ', 'LE'),
              ('left', 'PLUS', 'MINUS'),
              ('left', 'MUL', 'DIV'),
              ('right', 'UMINUS', 'NOT')
             )


def p_program(p):
    "program : stmt_list"
    state.ast = p[1]

def p_stmt_list(p):
    "stmt_list : stmt_list stmt"
    (STMTLIST, ll) = p[1]
    ll.append(p[2])
    p[0] = ('STMTLIST', ll)

def p_stmt_list_empty(p):
    "stmt_list : "
    p[0] = ('STMTLIST', list())

def p_stmt_assign(p):
    "stmt : ID '=' exp opt_semi"
    p[0] = ('ASSIGN', ('ID', p[1]), p[3])

def p_stmt_get(p):
    "stmt : GET ID opt_semi"
    p[0] = ('GET', ('ID', p[2]))

def p_stmt_put(p):
    "stmt : PUT exp opt_semi"
    p[0] = ('PUT', p[2])

def p_stmt_while(p):
    "stmt : WHILE '(' exp ')' stmt"
    p[0] = ('WHILE', p[3], p[5])

def p_stmt_if(p):
    "stmt : IF '(' exp ')' stmt"
    p[0] = ('IF', p[3], p[5], ('NIL',))

def p_stmt_ifelse(p):
    "stmt : IF '(' exp ')' stmt ELSE stmt"
    p[0] = ('IF', p[3], p[5], p[7])

def p_stmt_block(p):
    "stmt : '{' stmt_list '}'"
    p[0] = ('BLOCK', p[2])

def p_opt_semi(p):
    "opt_semi : ';'"
    pass

def p_opt_semi_empty(p):
    "opt_semi : "
    pass

def p_exp_plus(p):
    "exp : exp PLUS exp"
    p[0] = ('PLUS', p[1], p[3])

def p_exp_minus(p):
    "exp : exp MINUS exp"
    p[0] = ('MINUS', p[1], p[3])

def p_exp_mul(p):
    "exp : exp MUL exp"
    p[0] = ('MUL', p[1], p[3])

def p_exp_dic(p):
    "exp : exp DIV exp"
    p[0] = ('DIV', p[1], p[3])

def p_exp_eq(p):
    "exp : exp EQ exp"
    p[0] = ('EQ', p[1], p[3])

def p_exp_le(p):
    "exp : exp LE exp"
    p[0] = ('LE', p[1], p[3])

def p_exp_integer(p):
    "exp : INTEGER"
    p[0] = ('INTEGER', int(p[1]))

def p_exp_id(p):
    "exp : ID"
    p[0] = ('ID', p[1])

def p_exp_paren(p):
    "exp : '(' exp ')'"
    p[0] = p[2]

def p_exp_uminus(p):
    "exp : MINUS exp %prec UMINUS"
    if p[2][0] == 'INTEGER':
        p[0] = ('INTEGER', -p[2][1])
    else:
        p[0] = ('UMINUS', p[2])

def p_exp_not(p):
    "exp : NOT exp"
    if p[2][0] == 'INTEGER':
        p[0] = ('INTEGER', 0 if p[2][1] else 1)
    else:
        p[0] = ('NOT', p[2])

def p_error(t):
    raise SyntaxError("syntax error at '{}'".format(t.value))

### build the parser
parser = yacc.yacc()

if __name__ == "__main__":
    from sys import stdin
    from dumpast import dumpast
    char_stream = stdin.read()
    parser.parse(char_stream)
    dumpast(state.ast)
