'''
Syntax-directed interpreter for our Exp1 language
'''

symboltable = None

# stmt_list : {PRINT,STORE} (stmt)*
def stmt_list(stream):
  while stream.pointer().type in ['PRINT','STORE']:
    stmt(stream)
  return None

# stmt : {PRINT} PRINT exp SEMI
#      | {STORE} STORE var exp SEMI
def stmt(stream):
    token = stream.pointer()
    if token.type in ['PRINT']:
        stream.match('PRINT')
        val = exp(stream)
        stream.match('SEMI')
        print("{}".format(val))
        return None
    elif token.type in ['STORE']:
        global symboltable
        stream.match('STORE')
        name = var(stream)
        value = exp(stream)
        stream.match('SEMI')
        symboltable[name] = value
        return None
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
        vleft = exp(stream)
        vright = exp(stream)
        return vleft+vright
    elif token.type in ['MINUS']:
        stream.match('MINUS')
        vleft = exp(stream)
        vright = exp(stream)
        return vleft-vright
    elif token.type in ['LPAREN']:
        stream.match('LPAREN')
        v = exp(stream)
        stream.match('RPAREN')
        return v
    elif token.type in ['NAME']:
        global symboltable
        name = var(stream)
        return symboltable.get(name,0)
    elif token.type in ['NUMBER']:
        v = num(stream)
        return v
    else:
        raise SyntaxError("exp: syntax error at {}".format(token.value))

# var : {NAME} NAME
def var(stream):
    token = stream.pointer()
    if token.type in ['NAME']:
        stream.match('NAME')
        return token.value
    else:
        raise SyntaxError("var: syntax error at {}".format(token.value))

# num : {NUMBER} NUMBER
def num(stream):
    token = stream.pointer()
    if token.type in ['NUMBER']:
        stream.match('NUMBER')
        return int(token.value)
    else:
        raise SyntaxError("num: syntax error at {}".format(token.value))

# interpreter top-level driver
def interp(char_stream=None):
    from exp1_lexer import Lexer
    from sys import stdin
    global symboltable
    try:
        symboltable = dict()
        if not char_stream:
            char_stream = stdin.read() # read from stdin
        token_stream = Lexer(char_stream)
        stmt_list(token_stream) # call the parser function for start symbol
        if token_stream.end_of_file():
            print("done!")
        else:
            raise SyntaxError("parse: syntax error at {}"
                              .format(token_stream.pointer().value))
    except Exception as e:
        print("error: " + str(e))

if __name__ == "__main__":
    interp()
