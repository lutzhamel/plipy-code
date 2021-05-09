'''
Parser for our Exp1 language
'''

# stmtlist : {PRINT,STORE} (stmt)*
def stmtlist(stream):
  while stream.pointer().type in ['PRINT','STORE']:
    stmt(stream)
  return

# stmt : {PRINT} PRINT exp SEMI
#      | {STORE} STORE var exp SEMI
def stmt(stream):
    token = stream.pointer()
    if token.type in ['PRINT']:
        stream.match('PRINT')
        exp(stream)
        stream.match('SEMI')
        return
    elif token.type in ['STORE']:
        stream.match('STORE')
        var(stream)
        exp(stream)
        stream.match('SEMI')
        return
    else:
        raise SyntaxError("stmt: syntax error at {}".format(token.value))

# exp : {PLUS} PLUS exp exp
#     | {MINUS} MINUS exp exp
#     | {LPAREN} LPAREN exp RPAREN
#     | {NAME} var
#     | {NUMBER} num
def exp(stream):
    token = stream.pointer()
    if token.type in ['PLUS']:
        stream.match('PLUS')
        exp(stream)
        exp(stream)
        return
    elif token.type in ['MINUS']:
        stream.match('MINUS')
        exp(stream)
        exp(stream)
        return
    elif token.type in ['LPAREN']:
        stream.match('LPAREN')
        exp(stream)
        stream.match('RPAREN')
        return
    elif token.type in ['NAME']:
        var(stream)
        return
    elif token.type in ['NUMBER']:
        num(stream)
        return
    else:
        raise SyntaxError("exp: syntax error at {}".format(token.value))

# var : {NAME} NAME
def var(stream):
    token = stream.pointer()
    if token.type in ['NAME']:
        stream.match('NAME')
        return
    else:
        raise SyntaxError("var: syntax error at {}".format(token.value))

# num : {NUMBER} NUMBER
def num(stream):
    token = stream.pointer()
    if token.type in ['NUMBER']:
        stream.match('NUMBER')
        return
    else:
        raise SyntaxError("num: syntax error at {}".format(token.value))

# parser top-level driver
def parse(char_stream=None):
    from exp1_lexer import Lexer
    from sys import stdin
    try:
        if not char_stream:
            char_stream = stdin.read() # read from stdin
        token_stream = Lexer(char_stream)
        stmtlist(token_stream) # call the parser function for start symbol
        if token_stream.end_of_file():
            print("parse successful")
        else:
            raise SyntaxError("parse: syntax error at {}"
                              .format(token_stream.pointer().value))
    except Exception as e:
        print("error: " + str(e))

if __name__ == "__main__":
    parse()
