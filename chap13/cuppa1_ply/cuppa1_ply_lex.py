# Lexer for Cuppa1

from ply import lex

reserved = {
    'get'     : 'GET',
    'put'     : 'PUT',
    'if'      : 'IF',
    'else'    : 'ELSE',
    'while'   : 'WHILE',
    'not'     : 'NOT',
}

literals = [';','=','(',')','{','}']

tokens = [
          'PLUS','MINUS','MUL','DIV',
          'EQ','LE',
          'INTEGER','ID',
          ] + list(reserved.values())

t_ignore = ' \t'

def t_COMMENT(t):
    r'//.*'
    pass

def t_PLUS(t):
    r'\+'
    return t

def t_MINUS(t):
    r'-'
    return t

def t_MUL(t):
    r'\*'
    return t

def t_DIV(t):
    r'/'
    return t

def t_EQ(t):
    r'=='
    return t

def t_LE(t):
    r'=<'
    return t

def t_ID(t):
    r'[a-zA-Z_][a-zA-Z_0-9]*'
    t.type = reserved.get(t.value,'ID')    # Check for reserved words
    return t

def t_INTEGER(t):
    r'[0-9]+'
    return t

def t_NEWLINE(t):
    r'\n'
    pass

def t_error(t):
    raise ValueError("illegal character {}".format(t.value[0]))

# build the lexer
lexer = lex.lex(debug=0)
