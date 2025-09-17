'''
Lexer for our Exp2bytecode language
'''

import re

token_specs = [
#   type:          value:
    ('PRINT',      r'print'),
    ('STORE',      r'store'),
    ('INPUT',      r'input'),
    ('JUMPT',      r'jumpt'),
    ('JUMPF',      r'jumpf'),
    ('JUMP',       r'jump'),
    ('CALL',       r'call'),
    ('RETURN',     r'return'),
    ('PUSHV',      r'pushv'),
    ('POPV',       r'popv'),
    ('PUSHF',      r'pushf'),
    ('POPF',       r'popf'),
    ('STOP',       r'stop'),
    ('NOOP',       r'noop'),
    ('NUMBER',     r'[0-9]+'),
    ('STRING',     r'\".*\"'),
    ('NAME',       r'[a-zA-Z_\$][a-zA-Z0-9_\$]*'),
    ('RVX',        r'%rvx'),
    ('TSX',        r'%tsx'),
    ('ADD',        r'\+'),
    ('SUB',        r'-'),
    ('MUL',        r'\*'),
    ('DIV',        r'/'),
    ('NOT',        r'!'),
    ('EQ',         r'=='),
    ('LE',         r'=<'),
    ('LPAREN',     r'\('),
    ('RPAREN',     r'\)'),
    ('LSQUARE',    r'\['),
    ('RSQUARE',    r'\]'),
    ('SEMI',       r';'),
    ('COLON',      r':'),
    ('COMMENT',    r'#.*'),
    ('WHITESPACE', r'[ \t\n]+'),
    ('UNKNOWN',    r'.'),
]

# used for sanity checking in lexer.
token_types = set(type for (type,_) in token_specs)

class Token:
    def __init__(self,type,value):
        self.type = type
        self.value = value

    def __str__(self):
        return 'Token({},{})'.format(self.type,self.value)

def tokenize(code):
    tokens = []
    re_list = ['(?P<{}>{})'.format(type,re) for (type,re) in token_specs]
    combined_re = '|'.join(re_list)
    match_object_list = list(re.finditer(combined_re, code))
    for mo in match_object_list:
        type = mo.lastgroup
        value = mo.group()
        if type in ['STRING']:
            value = value[1:-1] # strip the quotes
        if type in ['WHITESPACE','COMMENT']:
            continue #ignore
        if type == 'UNKNOWN':
            raise ValueError("unexpected character '{}'".format(value))
        tokens.append(Token(type, value))
    tokens.append(Token('EOF', r'\eof'))
    return tokens

class Lexer:
    def __init__(self, input_string):
        self.tokens = tokenize(input_string)
        # the following is always valid because we will always have
        # at least the EOF token on the tokens list.
        self.curr_token_ix = 0

    def pointer(self):
        return self.tokens[self.curr_token_ix]

    def next(self):
        if not self.end_of_file():
            self.curr_token_ix += 1
        return self.pointer()

    def match(self, token_type):
        if token_type == self.pointer().type:
            tk = self.pointer()
            self.next()
            return tk
        elif token_type not in token_types:
            raise ValueError("unknown token type '{}'".format(token_type))
        else:
            raise SyntaxError('unexpected token {} while parsing, expected {}'
                              .format(self.pointer().type, token_type))

    def end_of_file(self):
        if self.pointer().type == 'EOF':
            return True
        else:
            return False

# test lexer
if __name__ == "__main__":

    prgm = \
    '''
    store x 1;
    print (+ x 1);
    '''
    lexer = Lexer(prgm)

    while not lexer.end_of_file():
        tok = lexer.pointer()
        print(tok)
        lexer.match(tok.type)
