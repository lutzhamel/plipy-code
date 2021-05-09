'''
Parser for our Cuppa5 language
'''
# stmt_list : ({VOID_TYPE,INTEGER_TYPE,FLOAT_TYPE,STRING_TYPE,ID,GET,PUT,RETURN,WHILE,IF,LCURLY} stmt)*
stmt_lookahead = [
    'VOID_TYPE',
    'INTEGER_TYPE',
    'FLOAT_TYPE',
    'STRING_TYPE',
    'ID',
    'GET',
    'PUT',
    'RETURN',
    'WHILE',
    'IF',
    'LCURLY',
    ]

def stmt_list(stream):
    while stream.pointer().type in stmt_lookahead:
        stmt(stream)
    return

# stmt : {VOID_TYPE} VOID_TYPE ID LPAREN ({INTEGER_TYPE,FLOAT_TYPE,STRING_TYPE} formal_args)? RPAREN stmt
#      | {INTEGER_TYPE,FLOAT_TYPE,STRING_TYPE} data_type ID decl_suffix
#      | {ID} ID id_suffix
#      | {GET} GET ID ({SEMI} SEMI)?
#      | {PUT} PUT exp ({SEMI} SEMI)?
#      | {RETURN} RETURN ({INTEGER,ID,LPAREN,MINUS,NOT} exp)? ({SEMI} SEMI)?
#      | {WHILE} WHILE LPAREN exp RPAREN stmt
#      | {IF} IF LPAREN exp RPAREN stmt ({ELSE} ELSE stmt)?
#      | {LCURLY} LCURLY stmt_list RCURLY
def stmt(stream):
    if stream.pointer().type in ['VOID_TYPE']:
        stream.match('VOID_TYPE')
        stream.match('ID')
        stream.match('LPAREN')
        if stream.pointer().type in ['INTEGER_TYPE','FLOAT_TYPE','STRING_TYPE']:
            formal_args(stream)
        stream.match('RPAREN')
        stmt(stream)
        return
    elif stream.pointer().type in ['INTEGER_TYPE','FLOAT_TYPE','STRING_TYPE']:
        data_type(stream)
        stream.match('ID')
        decl_suffix(stream)
        return
    elif stream.pointer().type in ['ID']:
        stream.match('ID')
        id_suffix(stream)
        return
    elif stream.pointer().type in ['GET']:
        stream.match('GET')
        stream.match('ID')
        if stream.pointer().type in ['SEMI']:
            stream.match('SEMI')
        return
    elif stream.pointer().type in ['PUT']:
        stream.match('PUT')
        exp(stream)
        if stream.pointer().type in ['SEMI']:
            stream.match('SEMI')
        return
    elif stream.pointer().type in ['RETURN']:
        stream.match('RETURN')
        if stream.pointer().type in exp_lookahead:
            exp(stream)
        if stream.pointer().type in ['SEMI']:
            stream.match('SEMI')
        return
    elif stream.pointer().type in ['WHILE']:
        stream.match('WHILE')
        stream.match('LPAREN')
        exp(stream)
        stream.match('RPAREN')
        stmt(stream)
        return
    elif stream.pointer().type in ['IF']:
        stream.match('IF')
        stream.match('LPAREN')
        exp(stream)
        stream.match(RPAREN)
        stmt(stream)
        if stream.pointer().type in ['ELSE']:
            stream.match('ELSE')
            stmt(stream)
            return
        else:
            return
    elif stream.pointer().type in ['LCURLY']:
        stream.match('LCURLY')
        stmt_list(stream)
        stream.match('RCURLY')
        return
    else:
        raise SyntaxError("stmt: syntax error at {}"
                          .format(stream.pointer().value))

# data_type : {INTEGER_TYPE,FLOAT_TYPE,STRING_TYPE} primitive_type
#                   ({LSQUARE} LSQUARE INTEGER RSQUARE)?
def data_type(stream):
    if stream.pointer().type in ['INTEGER_TYPE','FLOAT_TYPE','STRING_TYPE']:
        primitive_type(stream)
        if stream.pointer().type in ['LSQUARE']:
            stream.match('LSQUARE')
            stream.match('INTEGER')
            stream.match('RSQUARE')
        return
    else:
        raise SyntaxError("data_type: syntax error at {}"
                          .format(stream.pointer().value))


# primitive_type : {INTEGER_TYPE} INTEGER_TYPE
#                | {FLOAT_TYPE} FLOAT_TYPE
#                | {STRING_TYPE} STRING_TYPE
def primitive_type(stream):
    if stream.pointer().type in ['INTEGER_TYPE']:
        stream.match('INTEGER_TYPE')
        return
    elif stream.pointer().type in ['FLOAT_TYPE']:
        stream.match('FLOAT_TYPE')
        return
    elif stream.pointer().type in ['STRING_TYPE']:
        stream.match('STRING_TYPE')
        return
    else:
        raise SyntaxError("primitive_type: syntax error at {}"
                          .format(stream.pointer().value))


# decl_suffix : {LPAREN} LPAREN ({INTEGER_TYPE,FLOAT_TYPE,STRING_TYPE} formal_args)? RPAREN stmt
#             | {ASSIGN} ASSIGN
#                  ( {INTEGER,FLOAT,STRING,ID,LPAREN,MINUS,NOT} exp
#                    | {LCURLY} LCURLY exp ({COMMA} COMMA exp)* RCURLY )
#                  ({SEMI} SEMI)?
#             | ({SEMI} SEMI)?
def decl_suffix(stream):
    if stream.pointer().type in ['LPAREN']:
        stream.match('LPAREN')
        if stream.pointer().type in ['INTEGER_TYPE','FLOAT_TYPE','STRING_TYPE']:
            formal_args(stream)
        stream.match('RPAREN')
        stmt(stream)
        return
    elif stream.pointer().type in ['ASSIGN']:
        stream.match('ASSIGN')
        if stream.pointer().type in exp_lookahead:
            exp(stream)
        elif stream.pointer().type in ['LCURLY']:
            stream.match('LCURLY')
            exp(stream)
            while stream.pointer().type in ['COMMA']:
                stream.match('COMMA')
                exp(stream)
            stream.match('RCURLY')
        if stream.pointer().type in ['SEMI']:
            stream.match('SEMI')
        return
    else:
        if stream.pointer().type in ['SEMI']:
            stream.match('SEMI')
        return

# id_suffix : {LPAREN} LPAREN ({INTEGER,FLOAT,STRING,ID,LPAREN,MINUS,NOT} actual_args)? RPAREN
#                      ({LSQUARE} LSQUARE exp RSQUARE ASSIGN exp)?
#                      ({SEMI} SEMI)?
#           | {LSQUARE} LSQUARE exp RSQUARE ASSIGN exp ({SEMI} SEMI)?
#           | {ASSIGN} ASSIGN exp ({SEMI} SEMI)?
def id_suffix(stream):
    if stream.pointer().type in ['LPAREN']:
        stream.match('LPAREN')
        if stream.pointer().type in exp_lookahead:
            actual_args(stream)
        stream.match('RPAREN')
        if stream.pointer().type in ['LSQUARE']:
            stream.match('LSQUARE')
            exp(stream)
            stream.match('RSQUARE')
            stream.match('ASSIGN')
            exp(stream)
        if stream.pointer().type in ['SEMI']:
            stream.match('SEMI')
        return
    elif stream.pointer().type in ['LSQUARE']:
        stream.match('LSQUARE')
        exp(stream)
        stream.match('RSQUARE')
        stream.match('ASSIGN')
        exp(stream)
        if stream.pointer().type in ['SEMI']:
            stream.match('SEMI')
        return
    elif stream.pointer().type in ['ASSIGN']:
        stream.match('ASSIGN')
        exp(stream)
        if stream.pointer().type in ['SEMI']:
            stream.match('SEMI')
        return
    else:
        raise SyntaxError("id_suffix: syntax error at {}"
                          .format(stream.pointer().value))



# exp : {INTEGER,FLOAT,STRING,ID,LPAREN,MINUS,NOT} exp_low
# exp_lookahead
#   == exp_low_lookahead
#   == exp_med_lookahead
#   == exp_high_lookahead
#   == primary_lookahead
exp_lookahead = [
    'INTEGER',
    'FLOAT',
    'STRING',
    'ID',
    'LPAREN',
    'MINUS',
    'NOT',
    ]

def exp(stream):
    if stream.pointer().type in exp_lookahead:
        exp_low(stream)
        return
    else:
        raise SyntaxError("exp: syntax error at {}"
                          .format(stream.pointer().value))

# exp_low : {INTEGER,FLOAT,STRING,ID,LPAREN,MINUS,NOT} exp_med ({EQ,LE} (EQ|LE) exp_med)*
def exp_low(stream):
    if stream.pointer().type in exp_lookahead:
        exp_med(stream)
        while stream.pointer().type in ['EQ','LE']:
            if stream.pointer().type == 'EQ':
                stream.match('EQ')
            else:
                stream.match('LE')
            exp_med(stream)
        return
    else:
        raise SyntaxError("exp_low: syntax error at {}"
                          .format(stream.pointer().value))

# exp_med : {INTEGER,FLOAT,STRING,ID,LPAREN,MINUS,NOT} exp_high ({PLUS,MINUS} (PLUS|MINUS) exp_high)*
def exp_med(stream):
    if stream.pointer().type in exp_lookahead:
        exp_high(stream)
        while stream.pointer().type in ['PLUS','MINUS']:
            if stream.pointer().type == 'PLUS':
                stream.match('PLUS')
            else:
                stream.match('MINUS')
            exp_high(stream)
        return
    else:
        raise SyntaxError("exp_med: syntax error at {}"
                          .format(stream.pointer().value))

# exp_high : {INTEGER,FLOAT,STRING,ID,LPAREN,MINUS,NOT} primary ({MUL,DIV} (MUL|DIV) primary)*
def exp_high(stream):
    if stream.pointer().type in exp_lookahead:
        primary(stream)
        while stream.pointer().type in ['MUL','DIV']:
            if stream.pointer().type == 'MUL':
                stream.match('MUL')
            else:
                stream.match('DIV')
            primary(stream)
        return
    else:
        raise SyntaxError("exp_high: syntax error at {}"
                          .format(stream.pointer().value))

# primary : {INTEGER} INTEGER
#         | {FLOAT} FLOAT
#         | {STRING} STRING
#         | {ID} ID ({LPAREN,LSQUARE} id_exp_suffix)?
#         | {LPAREN} LPAREN exp RPAREN
#         | {MINUS} MINUS primary
#         | {NOT} NOT primary
def primary(stream):
    if stream.pointer().type in ['INTEGER']:
        stream.match('INTEGER')
        return
    elif stream.pointer().type in ['FLOAT']:
        stream.match('FLOAT')
        return
    elif stream.pointer().type in ['STRING']:
        stream.match('STRING')
        return
    elif stream.pointer().type in ['ID']:
        stream.match('ID')
        if stream.pointer().type in ['LPAREN','LSQUARE']:
            id_exp_suffix(stream)
        return
    elif stream.pointer().type in ['LPAREN']:
        stream.match('LPAREN')
        exp(stream)
        stream.match('RPAREN')
        return
    elif stream.pointer().type in ['MINUS']:
        stream.match('MINUS')
        primary(stream)
        return
    elif stream.pointer().type in ['NOT']:
        stream.match('NOT')
        primary(stream)
        return
    else:
        raise SyntaxError("primary: syntax error at {}"
                          .format(stream.pointer().value))

# id_exp_suffix : {LPAREN} LPAREN ({INTEGER,FLOAT,STRING,ID,LPAREN,MINUS,NOT} actual_args)? RPAREN
#                       ({LSQUARE} LSQUARE exp RSQUARE)?
#               | {LSQUARE} LSQUARE exp RSQUARE
def id_exp_suffix(stream):
    if stream.pointer().type in ['LPAREN']:
        stream.match('LPAREN')
        if stream.pointer().type in exp_lookahead:
            actual_args(stream)
        stream.match('RPAREN')
        if stream.pointer().type in ['LSQUARE']:
            stream.match('LSQUARE')
            exp(stream)
            stream.match('RSQUARE')
        return
    elif stream.pointer().type in ['LSQUARE']:
        stream.match('LSQUARE')
        exp(stream)
        stream.match('RSQUARE')
        return
    else:
        return

# formal_args : {INTEGER_TYPE,FLOAT_TYPE,STRING_TYPE} data_type ID ({COMMA} COMMA data_type ID)*
def formal_args(stream):
    if stream.pointer().type in ['INTEGER_TYPE','FLOAT_TYPE','STRING_TYPE']:
        data_type(stream)
        stream.match('ID')
        while stream.pointer().type in ['COMMA']:
            stream.match('COMMA')
            data_type(stream)
            stream.match('ID')
        return
    else:
        raise SyntaxError("formal_args: syntax error at {}"
                          .format(stream.pointer().value))

# actual_args : {INTEGER,FLOAT,STRING,ID,LPAREN,MINUS,NOT} exp ({COMMA} COMMA exp)*
def actual_args(stream):
    if stream.pointer().type in exp_lookahead:
        exp(stream)
        while stream.pointer().type in ['COMMA']:
            stream.match('COMMA')
            exp(stream)
        return
    else:
        raise SyntaxError("actual_args: syntax error at {}"
                          .format(stream.pointer().value))

# parser top-level driver
def parse(char_stream=None):
    from cuppa5_lexer import Lexer
    from sys import stdin
    try:
        if not char_stream:
            char_stream = stdin.read() # read from stdin
        token_stream = Lexer(char_stream)
        stmt_list(token_stream) # call the parser function for start symbol
        if token_stream.end_of_file():
            print("parse successful")
        else:
            raise SyntaxError("parse: syntax error at {}"
                              .format(token_stream.pointer().value))
    except Exception as e:
        print("error: " + str(e))

if __name__ == "__main__":
    parse()
