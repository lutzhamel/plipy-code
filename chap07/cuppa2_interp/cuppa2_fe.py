'''
Frontend for our Cuppa2 language - builds an AST where each
node is of the shape,

    (TYPE, [arg1, arg2, arg3,...])

here TYPE is a string describing the node type.
'''

# stmt_list : ({DECLARE,ID,GET,PUT,WHILE,IF,LCURLY} stmt)*
def stmt_list(stream):
    lst = []
    while stream.pointer().type in ['DECLARE','ID','GET','PUT','WHILE','IF','LCURLY']:
        s = stmt(stream)
        lst.append(s)
    return ('STMTLIST', lst)

# stmt : {DECLARE} DECLARE ID ({ASSIGN} ASSIGN exp)? ({SEMI} SEMI)?
#      | {ID} ID ASSIGN exp ({SEMI} SEMI)?
#      | {GET} GET ID ({SEMI} SEMI)?
#      | {PUT} PUT exp ({SEMI} SEMI)?
#      | {WHILE} WHILE LPAREN exp RPAREN stmt
#      | {IF} IF LPAREN exp RPAREN stmt ({ELSE} ELSE stmt)?
#      | {LCURLY} LCURLY stmt_list RCURLY
def stmt(stream):
    token = stream.pointer()
    if token.type in ['DECLARE']:
        stream.match('DECLARE')
        id_tk = stream.match('ID')
        if stream.pointer().type in ['ASSIGN']:
            stream.match('ASSIGN')
            e = exp(stream)
        else:
            # if no initializer assume default value
            e = ('INTEGER', 0)
        if stream.pointer().type in ['SEMI']:
            stream.match('SEMI')
        return ('DECLARE', ('ID', id_tk.value), e)
    elif token.type in ['ID']:
        id_tk = stream.match('ID')
        stream.match('ASSIGN')
        e = exp(stream)
        if stream.pointer().type in ['SEMI']:
            stream.match('SEMI')
        return ('ASSIGN', ('ID', id_tk.value), e)
    elif token.type in ['GET']:
        stream.match('GET')
        id_tk = stream.match('ID')
        if stream.pointer().type in ['SEMI']:
            stream.match('SEMI')
        return ('GET', ('ID', id_tk.value))
    elif token.type in ['PUT']:
        stream.match('PUT')
        e = exp(stream)
        if stream.pointer().type in ['SEMI']:
            stream.match('SEMI')
        return ('PUT', e)
    elif token.type in ['WHILE']:
        stream.match('WHILE')
        stream.match('LPAREN')
        e = exp(stream)
        stream.match('RPAREN')
        s = stmt(stream)
        return ('WHILE', e, s)
    elif token.type in ['IF']:
        stream.match('IF')
        stream.match('LPAREN')
        e = exp(stream)
        stream.match('RPAREN')
        s1 = stmt(stream)
        if stream.pointer().type in ['ELSE']:
            stream.match('ELSE')
            s2 = stmt(stream)
            return ('IF', e, s1, s2)
        else:
            return ('IF', e, s1, ('NIL',))
    elif token.type in ['LCURLY']:
        stream.match('LCURLY')
        sl = stmt_list(stream)
        stream.match('RCURLY')
        return ('BLOCK', sl)
    else:
        raise SyntaxError("stmt: syntax error at {}"
                          .format(stream.pointer().value))

# exp : {INTEGER,ID,LPAREN,MINUS,NOT} exp_low
def exp(stream):
    if stream.pointer().type in ['INTEGER','ID','LPAREN','MINUS','NOT']:
        e = exp_low(stream)
        return e
    else:
        raise SyntaxError("exp: syntax error at {}"
                          .format(stream.pointer().value))

# exp_low : {INTEGER,ID,LPAREN,MINUS,NOT} exp_med ({EQ,LE} (EQ|LE) exp_med)*
def exp_low(stream):
    if stream.pointer().type in ['INTEGER','ID','LPAREN','MINUS','NOT']:
        e = exp_med(stream)
        while stream.pointer().type in ['EQ','LE']:
            if stream.pointer().type == 'EQ':
                op_tk = stream.match('EQ')
            else:
                op_tk = stream.match('LE')
            tmp = exp_med(stream)
            e = (op_tk.type, e, tmp)
        return e
    else:
        raise SyntaxError("exp_low: syntax error at {}"
                          .format(stream.pointer().value))

# exp_med : {INTEGER,ID,LPAREN,MINUS,NOT} exp_high ({PLUS,MINUS} (PLUS|MINUS) exp_high)*
def exp_med(stream):
    if stream.pointer().type in ['INTEGER','ID','LPAREN','MINUS','NOT']:
        e = exp_high(stream)
        while stream.pointer().type in ['PLUS','MINUS']:
            if stream.pointer().type == 'PLUS':
                op_tk = stream.match('PLUS')
            else:
                op_tk = stream.match('MINUS')
            tmp = exp_high(stream)
            e = (op_tk.type, e, tmp)
        return e
    else:
        raise SyntaxError("exp_med: syntax error at {}"
                          .format(stream.pointer().value))

# exp_high : {INTEGER,ID,LPAREN,MINUS,NOT} primary ({MUL,DIV} (MUL|DIV) primary)*
def exp_high(stream):
    if stream.pointer().type in ['INTEGER','ID','LPAREN','MINUS','NOT']:
        e = primary(stream)
        while stream.pointer().type in ['MUL','DIV']:
            if stream.pointer().type == 'MUL':
                op_tk = stream.match('MUL')
            else:
                op_tk = stream.match('DIV')
            tmp = primary(stream)
            e = (op_tk.type, e, tmp)
        return e
    else:
        raise SyntaxError("exp_high: syntax error at {}"
                          .format(stream.pointer().value))

# primary : {INTEGER} INTEGER
#         | {ID} ID
#         | {LPAREN} LPAREN exp RPAREN
#         | {MINUS} MINUS primary
#         | {NOT} NOT primary
def primary(stream):
    if stream.pointer().type in ['INTEGER']:
        tk = stream.match('INTEGER')
        return ('INTEGER', int(tk.value))
    elif stream.pointer().type in ['ID']:
        tk = stream.match('ID')
        return ('ID', tk.value)
    elif stream.pointer().type in ['LPAREN']:
        stream.match('LPAREN')
        e = exp(stream)
        stream.match('RPAREN')
        return e
    elif stream.pointer().type in ['MINUS']:
        stream.match('MINUS')
        e = primary(stream)
        if e[0] == 'INTEGER':
            return ('INTEGER', -e[1])
        else:
            return ('UMINUS', e)
    elif stream.pointer().type in ['NOT']:
        stream.match('NOT')
        e = primary(stream)
        if e[0] == 'INTEGER':
            return ('INTEGER', 0 if e[1] else 1)
        else:
            return ('NOT', e)
    else:
        raise SyntaxError("primary: syntax error at {}"
                          .format(stream.pointer().value))

# frontend top-level driver
def parse(stream):
    from cuppa2_lexer import Lexer
    token_stream = Lexer(stream)
    sl = stmt_list(token_stream) # call the parser function for start symbol
    if not token_stream.end_of_file():
        raise SyntaxError("parse: syntax error at {}"
                          .format(token_stream.pointer().value))
    else:
        return sl
