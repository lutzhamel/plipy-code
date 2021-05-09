'''
Parser for our calc language

explist : ({ NUM, PLUS, MINUS, LPAREN } exp)*

exp  : { NUM } NUM
     | { PLUS, MINUS } op exp exp
     | { LPAREN } LPAREN op exp exp ({ NUM, PLUS, MINUS, LPAREN } exp)* RPAREN

op : { PLUS } PLUS
   | { MINUS } MINUS
'''

def explist(stream):
    while stream.pointer().type in ['NUM', 'PLUS', 'MINUS', 'LPAREN']:
        exp(stream)
    return

def exp(stream):
    token = stream.pointer()
    if token.type in ['NUM']:
        stream.match('NUM')
        return
    elif token.type in ['PLUS','MINUS']:
        op(stream)
        exp(stream)
        exp(stream)
        return
    elif token.type in ['LPAREN']:
        stream.match('LPAREN')
        op(stream)
        exp(stream)
        exp(stream)
        while stream.pointer().type in ['NUM', 'PLUS', 'MINUS', 'LPAREN']:
            exp(stream)
        stream.match('RPAREN')
    else:
        raise SyntaxError("syntax error at {}".format(token.type))

def op(stream):
    token = stream.pointer()
    if token.type in ['PLUS']:
        stream.match('PLUS')
        return
    elif token.type in ['MINUS']:
        stream.match('MINUS')
        return
    else:
        raise SyntaxError("syntax error at {}".format(token.type))

def parse():
    from calc_lexer import Lexer
    from sys import stdin
    try:
        char_stream = stdin.read() # read from stdin
        token_stream = Lexer(char_stream)
        explist(token_stream) # call the parser function for start symbol
        if token_stream.end_of_file():
            print("parse successful")
        else:
            raise SyntaxError("bad syntax at {}"
                              .format(token_stream.pointer()))
    except Exception as e:
        print("error: " + str(e))

if __name__ == "__main__":
    parse()
