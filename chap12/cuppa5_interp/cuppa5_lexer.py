'''
Lexer for our Cuppa5 language
'''

import re

token_specs = [
#   type:          value:
    ('COMMENT',       r'//.*'),
    ('GET',           r'get'),
    ('PUT',           r'put'),
    ('RETURN',        r'return'),
    ('WHILE',         r'while'),
    ('IF',            r'if'),
    ('ELSE',          r'else'),
    ('NOT',           r'not'),
    ('INTEGER_TYPE',  r'int'),
    ('FLOAT_TYPE',    r'float'),
    ('STRING_TYPE',   r'string'),
    ('VOID_TYPE',     r'void'),
    ('ID',            r'[a-zA-Z][a-zA-Z0-9_]*'),
    ('NUMBER',        r'([0-9]*[.])?[0-9]+'), # for INTEGER and FLOAT see below
    ('STRING',        r'\"[^\"]*\"'),
    ('PLUS',          r'\+'),
    ('MINUS',         r'-'),
    ('MUL',           r'\*'),
    ('DIV',           r'/'),
    ('EQ',            r'=='),
    ('LE',            r'=<'),
    ('ASSIGN',        r'='),
    ('LPAREN',        r'\('),
    ('RPAREN',        r'\)'),
    ('LCURLY',        r'{'),
    ('RCURLY',        r'}'),
    ('LSQUARE',       r'\['),
    ('RSQUARE',       r'\]'),
    ('SEMI',          r';'),
    ('COMMA',         r','),
    ('WHITESPACE',    r'[ \t\n]+'),
    ('UNKNOWN',       r'.'),
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
        if type in ['NUMBER']:
            type = 'FLOAT' if '.' in value else 'INTEGER'
            value = float(value) if type == 'FLOAT' else int(value)
        elif type in ['STRING']:
            value = value[1:-1] # strip the quotes
        elif type in ['WHITESPACE','COMMENT']:
            continue #ignore
        elif type == 'UNKNOWN':
            raise ValueError("unexpected character '{}'".format(value))
        tokens.append(Token(type, value))
    tokens.append(Token('EOF', '\eof'))
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
    from sys import stdin
    prgm = stdin.read()
    lexer = Lexer(prgm)
    while not lexer.end_of_file():
        tok = lexer.pointer()
        print(tok)
        lexer.match(tok.type)
