'''
Frontend for our Exp2bytecode interpreter
'''

from exp2bytecode_interp_state import state

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
        l = label_def(stream)
        i = instr(stream)
        state.label_table[l] = state.instr_ix
        state.program.append(i)
        state.instr_ix += 1
        return None
    elif stream.pointer().type in instr_lookahead:
        i = instr(stream)
        state.program.append(i)
        state.instr_ix += 1
        return None
    else:
        raise SyntaxError("labeled_instr: syntax error at {}"
                          .format(stream.pointer().value))

# label_def : {NAME} label COLON
def label_def(stream):
    if stream.pointer().type in ['NAME']:
        l = label(stream)
        stream.match('COLON')
        return l
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
            s = stream.match('STRING').value
        else:
            s = None
        e = exp(stream)
        stream.match('SEMI')
        return ('PRINT', s, e)
    elif stream.pointer().type in ['INPUT']:
        stream.match('INPUT')
        if stream.pointer().type in ['STRING']:
            s = stream.match('STRING').value
        else:
            s = None
        v = storable(stream)
        stream.match('SEMI')
        return ('INPUT', s, v)
    elif stream.pointer().type in ['STORE']:
        stream.match('STORE')
        s = storable(stream)
        e = exp(stream)
        stream.match('SEMI')
        return ('STORE', s, e)
    elif stream.pointer().type in ['JUMPT']:
        stream.match('JUMPT')
        e = exp(stream)
        l = label(stream)
        stream.match('SEMI')
        return ('JUMPT', e, l)
    elif stream.pointer().type in ['JUMPF']:
        stream.match('JUMPF')
        e = exp(stream)
        l = label(stream)
        stream.match('SEMI')
        return ('JUMPF', e, l)
    elif stream.pointer().type in ['JUMP']:
        stream.match('JUMP')
        l = label(stream)
        stream.match('SEMI')
        return ('JUMP', l)
    elif stream.pointer().type in ['CALL']:
        stream.match('CALL')
        l = label(stream)
        stream.match('SEMI')
        return ('CALL', l)
    elif stream.pointer().type in ['RETURN']:
        stream.match('RETURN')
        stream.match('SEMI')
        return ('RETURN',)
    elif stream.pointer().type in ['PUSHV']:
        stream.match('PUSHV')
        e = exp(stream)
        stream.match('SEMI')
        return ('PUSHV', e)
    elif stream.pointer().type in ['POPV']:
        stream.match('POPV')
        if stream.pointer().type in ['NAME','RVX','TSX']:
            s = storable(stream)
        else:
            s = None
        stream.match('SEMI')
        return ('POPV', s)
    elif stream.pointer().type in ['PUSHF']:
        stream.match('PUSHF')
        s = size(stream)
        stream.match('SEMI')
        return ('PUSHF', s)
    elif stream.pointer().type in ['POPF']:
        stream.match('POPF')
        s = size(stream)
        stream.match('SEMI')
        return ('POPF', s)
    elif stream.pointer().type in ['STOP']:
        stream.match('STOP')
        stream.match('SEMI')
        return ('STOP',)
    elif stream.pointer().type in ['NOOP']:
        stream.match('NOOP')
        stream.match('SEMI')
        return ('NOOP',)
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
        e1 = exp(stream)
        e2 = exp(stream)
        return ('ADD', e1, e2)
    elif stream.pointer().type in ['SUB']:
        stream.match('SUB')
        e1 = exp(stream)
        if stream.pointer().type in exp_lookahead:
            e2 = exp(stream)
            return ('SUB', e1, e2)
        else:
            return ('UMINUS', e1)
    elif stream.pointer().type in ['MUL']:
        stream.match('MUL')
        e1 = exp(stream)
        e2 = exp(stream)
        return ('MUL', e1, e2)
    elif stream.pointer().type in ['DIV']:
        stream.match('DIV')
        e1 = exp(stream)
        e2 = exp(stream)
        return ('DIV', e1, e2)
    elif stream.pointer().type in ['NOT']:
        stream.match('NOT')
        e = exp(stream)
        return ('NOT', e)
    elif stream.pointer().type in ['EQ']:
        stream.match('EQ')
        e1 = exp(stream)
        e2 = exp(stream)
        return ('EQ', e1, e2)
    elif stream.pointer().type in ['LE']:
        stream.match('LE')
        e1 = exp(stream)
        e2 = exp(stream)
        return ('LE', e1, e2)
    elif stream.pointer().type in ['LPAREN']:
        stream.match('LPAREN')
        e1 = exp(stream)
        stream.match('RPAREN')
        return e1
    elif stream.pointer().type in ['NAME','RVX','TSX']:
        s = storable(stream)
        return s
    elif stream.pointer().type in ['NUMBER']:
        n = num(stream)
        return ('NUMBER', n)
    else:
        raise SyntaxError("exp: syntax error at {}"
                          .format(stream.pointer().value))

# storable : {NAME} var
#          | {RVX} RVX
#          | {TSX} TSX ({LSQUARE} offset)?
def storable(stream):
    if stream.pointer().type in ['NAME']:
        v = var(stream)
        return ('ID', v)
    elif stream.pointer().type in ['RVX']:
        stream.match('RVX')
        return ('RVX',)
    elif stream.pointer().type in ['TSX']:
        stream.match('TSX')
        if stream.pointer().type in ['LSQUARE']:
            o = offset(stream)
        else:
            o = None
        return ('TSX', o)
    else:
        raise SyntaxError("storable: syntax error at {}"
                          .format(stream.pointer().value))

# offset : {LSQUARE} LSQUARE exp RSQUARE
def offset(stream):
    if stream.pointer().type in ['LSQUARE']:
        stream.match('LSQUARE')
        e = exp(stream)
        stream.match('RSQUARE')
        return e
    else:
        raise SyntaxError("offset: syntax error at {}"
                          .format(stream.pointer().value))

# size  : {ADD,SUB,MUL,DIV,NOT,EQ,LE,LPAREN,NAME,RVX,TSX,NUMBER} exp
def size(stream):
    if stream.pointer().type in exp_lookahead:
        e = exp(stream)
        return e
    else:
        raise SyntaxError("size: syntax error at {}"
                          .format(stream.pointer().value))

# label : {NAME} NAME
def label(stream):
    if stream.pointer().type in ['NAME']:
        n = stream.match('NAME').value
        return n
    else:
        raise SyntaxError("label: syntax error at {}"
                          .format(stream.pointer().value))

# var : {NAME} NAME
def var(stream):
    if stream.pointer().type in ['NAME']:
        n = stream.match('NAME').value
        return n
    else:
        raise SyntaxError("var: syntax error at {}"
                          .format(stream.pointer().value))

# num : {NUMBER} NUMBER
def num(stream):
    if stream.pointer().type in ['NUMBER']:
        n = stream.match('NUMBER').value
        return n
    else:
        raise SyntaxError("num: syntax error at {}"
                          .format(stream.pointer().value))

# parser top-level driver
def parse(stream):
    from exp2bytecode_lexer import Lexer
    token_stream = Lexer(stream)
    instr_list(token_stream) # call the parser function for start symbol
    if not token_stream.end_of_file():
        raise SyntaxError("parse: syntax error at {}"
                          .format(token_stream.pointer().value))
