# Lexer for pattern language

from ply import lex

literals = ['=', '(', ')']
tokens = ['ID']
t_ignore = ' \t'

def t_ID(t):
    r'[a-zA-Z_][a-zA-Z_0-9]*'
    return t

def t_NEWLINE(t):
    r'\n'
    pass

def t_COMMENT(t):
    r'\#.*'
    pass

def t_error(t):
    raise ValueError("illegal character {}".format(t.value[0]))

# build the lexer
lexer = lex.lex(debug=0)
