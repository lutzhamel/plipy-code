'''
Parser for our Exp1bytecode language
'''
# lookahead sets for parser
exp_lookahead = [
    'ADD',
    'SUB',
    'MUL',
    'DIV',
    'NOT',
    'EQ',
    'LE',
    'LPAREN',
    'NAME',
    'RVX',
    'TSX',
    'NUMBER',
    ]

instr_lookahead = [
    'PRINT',
    'STORE',
    'INPUT',
    'JUMPT',
    'JUMPF',
    'JUMP',
    'CALL',
    'RETURN',
    'PUSHV',
    'POPV',
    'PUSHF',
    'POPF',
    'STOP',
    'NOOP',
    ]

labeled_instr_lookahead = instr_lookahead + ['NAME']

# instr_list : ({NAME,PRINT,STORE,INPUT,JUMPT,JUMPF,JUMP,CALL,RETURN,PUSHV,POPV,PUSHF,POPF,STOP,NOOP} labeled_instr)*
def instr_list(stream):
  while stream.pointer().type in labeled_instr_lookahead:
    labeled_instr(stream)
  return

# labeled_instr : {NAME} label_def instr
#               | {PRINT,STORE,INPUT,JUMPT,JUMPF,JUMP,CALL,RETURN,PUSHV,POPV,PUSHF,POPF,STOP,NOOP} instr
def labeled_instr(stream):
    if stream.pointer().type in ['NAME']:
        label_def(stream)
        instr(stream)
        return
    elif stream.pointer().type in instr_lookahead:
        instr(stream)
        return
    else:
        raise SyntaxError("labeled_instr: syntax error at {}"
                          .format(stream.pointer().value))

# label_def : {NAME} label COLON
def label_def(stream):
    if stream.pointer().type in ['NAME']:
        label(stream)
        stream.match('COLON')
        return
    else:
        raise SyntaxError("label_def: syntax error at {}"
                          .format(stream.pointer().value))

# instr : {PRINT} PRINT ({STRING} STRING)? exp SEMI
#       | {INPUT} INPUT ({STRING} STRING)? storable SEMI
#       | {STORE} STORE storable exp SEMI
#       | {JUMPT} JUMPT exp label SEMI
#       | {JUMPF} JUMPF exp label SEMI
#       | {JUMP} JUMP label SEMI
#       | {CALL} CALL label SEMI
#       | {RETURN} RETURN SEMI
#       | {PUSHV} PUSHV exp SEMI
#       | {POPV} POPV ({NAME,RVX,TSX} storable)? SEMI
#       | {PUSHF} PUSHF size SEMI
#       | {POPF} POPF size SEMI
#       | {STOP} STOP SEMI
#       | {NOOP} NOOP SEMI
def instr(stream):
    if stream.pointer().type in ['PRINT']:
        stream.match('PRINT')
        if stream.pointer().type in ['STRING']:
            stream.match('STRING')
        exp(stream)
        stream.match('SEMI')
        return
    elif stream.pointer().type in ['INPUT']:
        stream.match('INPUT')
        if stream.pointer().type in ['STRING']:
            stream.match('STRING')
        storable(stream)
        stream.match('SEMI')
        return
    elif stream.pointer().type in ['STORE']:
        stream.match('STORE')
        storable(stream)
        exp(stream)
        stream.match('SEMI')
        return
    elif stream.pointer().type in ['JUMPT']:
        stream.match('JUMPT')
        exp(stream)
        label(stream)
        stream.match('SEMI')
        return
    elif stream.pointer().type in ['JUMPF']:
        stream.match('JUMPF')
        exp(stream)
        label(stream)
        stream.match('SEMI')
        return
    elif stream.pointer().type in ['JUMP']:
        stream.match('JUMP')
        label(stream)
        stream.match('SEMI')
        return
    elif stream.pointer().type in ['CALL']:
        stream.match('CALL')
        label(stream)
        stream.match('SEMI')
        return
    elif stream.pointer().type in ['RETURN']:
        stream.match('RETURN')
        stream.match('SEMI')
        return
    elif stream.pointer().type in ['PUSHV']:
        stream.match('PUSHV')
        exp(stream)
        stream.match('SEMI')
        return
    elif stream.pointer().type in ['POPV']:
        stream.match('POPV')
        if stream.pointer().type in ['NAME','RVX','TSX']:
            storable(stream)
        stream.match('SEMI')
        return
    elif stream.pointer().type in ['PUSHF']:
        stream.match('PUSHF')
        size(stream)
        stream.match('SEMI')
        return
    elif stream.pointer().type in ['POPF']:
        stream.match('POPF')
        size(stream)
        stream.match('SEMI')
        return
    elif stream.pointer().type in ['STOP']:
        stream.match('STOP')
        stream.match('SEMI')
        return
    elif stream.pointer().type in ['NOOP']:
        stream.match('NOOP')
        stream.match('SEMI')
        return
    else:
        raise SyntaxError("instr: syntax error at {}"
                          .format(stream.pointer().value))

# exp : {ADD} ADD exp exp
#     | {SUB} SUB exp ({ADD,SUB,MUL,DIV,NOT,EQ,LE,LPAREN,NAME,RVX,TSX,NUMBER} exp)?
#     | {MUL} MUL exp exp
#     | {DIV} DIV exp exp
#     | {NOT} NOT exp
#     | {EQ} EQ exp exp
#     | {LE} LE exp exp
#     | {LPAREN} LPAREN exp RPAREN
#     | {NAME,RVX,TSX} storable
#     | {NUMBER} num
def exp(stream):
    if stream.pointer().type in ['ADD']:
        stream.match('ADD')
        exp(stream)
        exp(stream)
        return
    elif stream.pointer().type in ['SUB']:
        stream.match('SUB')
        exp(stream)
        if stream.pointer().type in exp_lookahead:
            exp(stream)
            return
        else:
            return
    elif stream.pointer().type in ['MUL']:
        stream.match('MUL')
        exp(stream)
        exp(stream)
        return
    elif stream.pointer().type in ['DIV']:
        stream.match('DIV')
        exp(stream)
        exp(stream)
        return
    elif stream.pointer().type in ['NOT']:
        stream.match('NOT')
        exp(stream)
        return
    elif stream.pointer().type in ['EQ']:
        stream.match('EQ')
        exp(stream)
        exp(stream)
        return
    elif stream.pointer().type in ['LE']:
        stream.match('LE')
        exp(stream)
        exp(stream)
        return
    elif stream.pointer().type in ['LPAREN']:
        stream.match('LPAREN')
        exp(stream)
        stream.match('RPAREN')
        return
    elif stream.pointer().type in ['NAME','RVX','TSX']:
        storable(stream)
        return
    elif stream.pointer().type in ['NUMBER']:
        num(stream)
        return
    else:
        raise SyntaxError("exp: syntax error at {}"
                          .format(stream.pointer().value))

# storable : {NAME} var
#          | {RVX} RVX
#          | {TSX} TSX ({LSQUARE} offset)?
def storable(stream):
    if stream.pointer().type in ['NAME']:
        var(stream)
        return
    elif stream.pointer().type in ['RVX']:
        stream.match('RVX')
        return
    elif stream.pointer().type in ['TSX']:
        stream.match('TSX')
        if stream.pointer().type in ['LSQUARE']:
            offset(stream)
        return
    else:
        raise SyntaxError("storable: syntax error at {}"
                          .format(stream.pointer().value))

# offset : {LSQUARE} LSQUARE exp RSQUARE
def offset(stream):
    if stream.pointer().type in ['LSQUARE']:
        stream.match('LSQUARE')
        exp(stream)
        stream.match('RSQUARE')
        return
    else:
        raise SyntaxError("offset: syntax error at {}"
                          .format(stream.pointer().value))

# size  : {ADD,SUB,MUL,DIV,NOT,EQ,LE,LPAREN,NAME,RVX,TSX,NUMBER} exp
def size(stream):
    if stream.pointer().type in exp_lookahead:
        exp(stream)
        return
    else:
        raise SyntaxError("size: syntax error at {}"
                          .format(stream.pointer().value))

# label : {NAME} NAME
def label(stream):
    if stream.pointer().type in ['NAME']:
        stream.match('NAME')
        return
    else:
        raise SyntaxError("label: syntax error at {}"
                          .format(stream.pointer().value))

# var : {NAME} NAME
def var(stream):
    if stream.pointer().type in ['NAME']:
        stream.match('NAME')
        return
    else:
        raise SyntaxError("var: syntax error at {}"
                          .format(stream.pointer().value))

# num : {NUMBER} NUMBER
def num(stream):
    if stream.pointer().type in ['NUMBER']:
        stream.match('NUMBER')
        return
    else:
        raise SyntaxError("num: syntax error at {}"
                          .format(stream.pointer().value))

# parser top-level driver
def parse(char_stream=None):
    from exp2bytecode_lexer import Lexer
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
