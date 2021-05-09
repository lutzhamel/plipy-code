'''
Frontend for our Exp1bytecode interpreter
'''

from exp1bytecode_interp_state import state

# lookahead sets for parser
exp_lookahead = ['ADD','SUB','MUL','DIV','NOT','EQ','LE','LPAREN','NAME','NUMBER']
instr_lookahead = ['PRINT','STORE','INPUT','JUMPT','JUMPF','JUMP','STOP','NOOP']
labeled_instr_lookahead = instr_lookahead + ['NAME']

# instr_list : ({NAME,PRINT,STORE,JUMPT,JUMPF,JUMP,STOP,NOOP} labeled_instr)*
def instr_list(stream):
  while stream.pointer().type in labeled_instr_lookahead:
    labeled_instr(stream)
  return None

# labeled_instr : {NAME} label_def instr
#               | {PRINT,STORE,JUMPT,JUMPF,JUMP,STOP,NOOP} instr
def labeled_instr(stream):
    token = stream.pointer()
    if token.type in ['NAME']:
        l = label_def(stream)
        i = instr(stream)
        state.label_table[l] = state.instr_ix
        state.program.append(i)
        state.instr_ix += 1
        return None
    elif token.type in instr_lookahead:
        i = instr(stream)
        state.program.append(i)
        state.instr_ix += 1
        return None
    else:
        raise SyntaxError("labeled_instr: syntax error at {}"
                          .format(token.value))

# label_def : {NAME} label COLON
def label_def(stream):
    token = stream.pointer()
    if token.type in ['NAME']:
        l = label(stream)
        stream.match('COLON')
        return l
    else:
        raise SyntaxError("label_def: syntax error at {}"
                          .format(token.value))

# instr : {PRINT} PRINT exp SEMI
#       | {STORE} STORE var exp SEMI
#       | {INPUT} INPUT var SEMI
#       | {JUMPT} JUMPT exp label SEMI
#       | {JUMPF} JUMPF exp label SEMI
#       | {JUMP} JUMP label SEMI
#       | {STOP} STOP SEMI
#       | {NOOP} NOOP SEMI
def instr(stream):
    token = stream.pointer()
    if token.type in ['PRINT']:
        stream.match('PRINT')
        e = exp(stream)
        stream.match('SEMI')
        return ('PRINT', e)
    elif token.type in ['STORE']:
        stream.match('STORE')
        v = var(stream)
        e = exp(stream)
        stream.match('SEMI')
        return ('STORE', v, e)
    elif token.type in ['INPUT']:
        stream.match('INPUT')
        v = var(stream)
        stream.match('SEMI')
        return ('INPUT', v)
    elif token.type in ['JUMPT']:
        stream.match('JUMPT')
        e = exp(stream)
        l = label(stream)
        stream.match('SEMI')
        return ('JUMPT', e , l)
    elif token.type in ['JUMPF']:
        stream.match('JUMPF')
        e = exp(stream)
        l = label(stream)
        stream.match('SEMI')
        return ('JUMPF', e, l)
    elif token.type in ['JUMP']:
        stream.match('JUMP')
        l = label(stream)
        stream.match('SEMI')
        return ('JUMP', l)
    elif token.type in ['STOP']:
        stream.match('STOP')
        stream.match('SEMI')
        return ('STOP',)
    elif token.type in ['NOOP']:
        stream.match('NOOP')
        stream.match('SEMI')
        return ('NOOP',)
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
        e1 = exp(stream)
        e2 = exp(stream)
        return ('ADD', e1, e2)
    elif token.type in ['SUB']:
        stream.match('SUB')
        e1 = exp(stream)
        if stream.pointer().type in exp_lookahead:
            e2 = exp(stream)
            return ('SUB', e1, e2)
        else:
            return ('UMINUS', e1)
    elif token.type in ['MUL']:
        stream.match('MUL')
        e1 = exp(stream)
        e2 = exp(stream)
        return ('MUL', e1, e2)
    elif token.type in ['DIV']:
        stream.match('DIV')
        e1 = exp(stream)
        e2 = exp(stream)
        return ('DIV', e1, e2)
    elif token.type in ['NOT']:
        stream.match('NOT')
        e = exp(stream)
        return ('NOT', e)
    elif token.type in ['EQ']:
        stream.match('EQ')
        e1 = exp(stream)
        e2 = exp(stream)
        return ('EQ', e1, e2)
    elif token.type in ['LE']:
        stream.match('LE')
        e1 = exp(stream)
        e2 = exp(stream)
        return ('LE', e1, e2)
    elif token.type in ['LPAREN']:
        stream.match('LPAREN')
        e1 = exp(stream)
        stream.match('RPAREN')
        return e1
    elif token.type in ['NAME']:
        v = var(stream)
        return ('NAME', v)
    elif token.type in ['NUMBER']:
        n = num(stream)
        return ('NUMBER', n)
    else:
        raise SyntaxError("exp: syntax error at {}"
                          .format(token.value))

# label : {NAME} NAME
def label(stream):
    token = stream.pointer()
    if token.type in ['NAME']:
        stream.match('NAME')
        return token.value
    else:
        raise SyntaxError("label: syntax error at {}"
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

# parser top-level driver
def parse(stream):
    from exp1bytecode_lexer import Lexer
    token_stream = Lexer(stream)
    instr_list(token_stream) # call the parser function for start symbol
    if not token_stream.end_of_file():
        raise SyntaxError("parse: syntax error at {}"
                          .format(token_stream.pointer().value))
