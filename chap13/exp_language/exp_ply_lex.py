# Lex specification for exp grammar

from ply import lex

tokens = ['ID', 'PLUS']

t_ignore = ' \t'

def t_PLUS(t):
    r'\+'
    return t

def t_ID(t):
    r'x|y'
    return t

def t_NEWLINE(t):
    r'\n'
    pass

def t_error(t):
        raise ValueError("illegal character '{}'"
                    .format(t.value[0]))

# build the lexer
lexer = lex.lex()
