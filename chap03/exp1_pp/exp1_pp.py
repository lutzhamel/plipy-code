'''
Pretty printer for our Exp1 language
'''

# stmt_list : {PRINT,STORE} (stmt)*
def stmt_list(stream):
  output_str = ""
  while stream.pointer().type in ['PRINT','STORE']:
    output_str += stmt(stream)
  return output_str

# stmt : {PRINT} PRINT exp SEMI
#      | {STORE} STORE var exp SEMI
def stmt(stream):
    token = stream.pointer()
    if token.type in ['PRINT']:
        stream.match('PRINT')
        e = exp(stream)
        stream.match('SEMI')
        return token.value+" "+e+";\n"
    elif token.type in ['STORE']:
        stream.match('STORE')
        n = var(stream)
        e = exp(stream)
        stream.match('SEMI')
        return token.value+" "+n+" "+e+";\n"
    else:
        raise SyntaxError("stmt: syntax error at {}"
                          .format(token.value))

# exp : {PLUS} PLUS exp exp
#     | {MINUS} MINUS exp exp
#     | {LPAREN} LPAREN exp RPAREN
#     | {NAME} var
#     | {NUMBER} num
def exp(stream):
    token = stream.pointer()
    if token.type in ['PLUS']:
        stream.match('PLUS')
        v1 = exp(stream)
        v2 = exp(stream)
        return "("+token.value+" "+v1+" "+v2+")"
    elif token.type in ['MINUS']:
        stream.match('MINUS')
        v1 = exp(stream)
        v2 = exp(stream)
        return "("+token.value+" "+v1+" "+v2+")"
    elif token.type in ['LPAREN']:
        stream.match('LPAREN')
        v = exp(stream)
        stream.match('RPAREN')
        return v
    elif token.type in ['NAME']:
        v = var(stream)
        return v
    elif token.type in ['NUMBER']:
        v = num(stream)
        return v
    else:
        raise SyntaxError("exp: syntax error at {}"
                          .format(token.value))

# var : {NAME} NAME
def var(stream):
    token = stream.pointer()
    if token.type in ['NAME']:
        stream.match('NAME')
        return token.value
    else:
        raise SyntaxError("var: syntax error at {}"
                          .format(token.value))

# num : {NUMBER} NUMBER
def num(stream):
    token = stream.pointer()
    if token.type in ['NUMBER']:
        stream.match('NUMBER')
        return token.value
    else:
        raise SyntaxError("num: syntax error at {}"
                          .format(token.value))

# top-level driver for pretty printer
def pp(char_stream=None):
    from exp1_lexer import Lexer
    from sys import stdin
    try:
        if not char_stream:
            char_stream = stdin.read() # read from stdin
        token_stream = Lexer(char_stream)
        formatted_string = stmt_list(token_stream)
        if token_stream.end_of_file():
            print("{}".format(formatted_string),end="")
        else:
            raise SyntaxError("parse: syntax error at {}"
                              .format(token_stream.pointer().value))
    except Exception as e:
        print("error: " + str(e))

if __name__ == "__main__":
    pp()
