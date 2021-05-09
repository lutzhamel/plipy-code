'''
Parser for our Exp1bytecode language
'''
# lookahead sets for parser
exp_lookahead = ['ADD','SUB','MUL','DIV','NOT','EQ','LE','LPAREN','NAME','NUMBER']
instr_lookahead = ['PRINT','STORE','JUMPT','JUMPF','JUMP','STOP','NOOP']
labeled_instr_lookahead = instr_lookahead + ['NAME']

# instr_list : ({NAME,PRINT,STORE,JUMPT,JUMPF,JUMP,STOP,NOOP} labeled_instr)*
def instr_list(stream):
  while stream.pointer().type in labeled_instr_lookahead:
    labeled_instr(stream)
  return

# labeled_instr : {NAME} label_def instr
#               | {PRINT,STORE,JUMPT,JUMPF,JUMP,STOP,NOOP} instr
def labeled_instr(stream):
    token = stream.pointer()
    if token.type in ['NAME']:
        label_def(stream)
        instr(stream)
        return
    elif token.type in instr_lookahead:
        instr(stream)
        return
    else:
        raise SyntaxError("labeled_instr: syntax error at {}"
                          .format(token.value))

# label_def : {NAME} label COLON
def label_def(stream):
    token = stream.pointer()
    if token.type in ['NAME']:
        label(stream)
        stream.match('COLON')
        return
    else:
        raise SyntaxError("label_def: syntax error at {}"
                          .format(token.value))

# instr : {PRINT} PRINT exp SEMI
#       | {STORE} STORE var exp SEMI
#       | {JUMPT} JUMPT exp label SEMI
#       | {JUMPF} JUMPF exp label SEMI
#       | {JUMP} JUMP label SEMI
#       | {STOP} STOP SEMI
#       | {NOOP} NOOP SEMI
def instr(stream):
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
    elif token.type in ['JUMPT']:
        stream.match('JUMPT')
        exp(stream)
        label(stream)
        stream.match('SEMI')
        return
    elif token.type in ['JUMPF']:
        stream.match('JUMPF')
        exp(stream)
        label(stream)
        stream.match('SEMI')
        return
    elif token.type in ['JUMP']:
        stream.match('JUMP')
        label(stream)
        stream.match('SEMI')
        return
    elif token.type in ['STOP']:
        stream.match('STOP')
        stream.match('SEMI')
        return
    elif token.type in ['NOOP']:
        stream.match('NOOP')
        stream.match('SEMI')
        return
    else:
        raise SyntaxError("instr: syntax error at {}"
                          .format(token.value))

# exp : {ADD} ADD exp exp
#     | {SUB} SUB exp ({ADD,SUB,MUL,DIV,NOT,EQ,LE,LPAREN,NAME,NUMBER} exp)?
#     | {MUL} MUL exp exp
#     | {DIV} DIV exp exp
#     | {NOT} NOT exp
#     | {EQ} EQ exp exp
#     | {LE} LE exp exp
#     | {LPAREN} LPAREN exp RPAREN
#     | {NAME} var
#     | {NUMBER} num
def exp(stream):
    token = stream.pointer()
    if token.type in ['ADD']:
        stream.match('ADD')
        exp(stream)
        exp(stream)
        return
    elif token.type in ['SUB']:
        stream.match('SUB')
        exp(stream)
        if stream.pointer().type in exp_lookahead:
            exp(stream)
            return
        else:
            return
    elif token.type in ['MUL']:
        stream.match('MUL')
        exp(stream)
        exp(stream)
        return
    elif token.type in ['DIV']:
        stream.match('DIV')
        exp(stream)
        exp(stream)
        return
    elif token.type in ['NOT']:
        stream.match('NOT')
        exp(stream)
        return
    elif token.type in ['EQ']:
        stream.match('EQ')
        exp(stream)
        exp(stream)
        return
    elif token.type in ['LE']:
        stream.match('LE')
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
        raise SyntaxError("exp: syntax error at {}"
                          .format(token.value))

# label : {NAME} NAME
def label(stream):
    token = stream.pointer()
    if token.type in ['NAME']:
        stream.match('NAME')
        return
    else:
        raise SyntaxError("label: syntax error at {}"
                          .format(token.value))

# var : {NAME} NAME
def var(stream):
    token = stream.pointer()
    if token.type in ['NAME']:
        stream.match('NAME')
        return
    else:
        raise SyntaxError("var: syntax error at {}"
                          .format(token.value))

# num : {NUMBER} NUMBER
def num(stream):
    token = stream.pointer()
    if token.type in ['NUMBER']:
        stream.match('NUMBER')
        return
    else:
        raise SyntaxError("num: syntax error at {}"
                          .format(token.value))

# parser top-level driver
def parse(char_stream=None):
    from exp1bytecode_lexer import Lexer
    from sys import stdin
    try:
        if not char_stream:
            char_stream = stdin.read() # read from stdin
        token_stream = Lexer(char_stream)
        instr_list(token_stream) # call the parser function for start symbol
        if token_stream.end_of_file():
            print("parse successful")
        else:
            raise SyntaxError("parse: syntax error at {}"
                              .format(token_stream.pointer().value))
    except Exception as e:
        print("error: " + str(e))

if __name__ == "__main__":
    parse()
