'''
Parser for sLL(1) grammar:

exp : {+} + exp exp
    | {x,y} var

var : {x} x
    | {y} y
'''

def exp(stream):
    sym = stream.pointer()
    if sym in ['+']:
        stream.match('+')
        exp(stream)
        exp(stream)
        return
    elif sym in ['x','y']:
        var(stream)
        return
    else:
        raise SyntaxError('unexpected symbol {}'.format(sym))

def var(stream):
    sym = stream.pointer()
    if sym in ['x']:
        stream.match('x')
        return
    elif sym in ['y']:
        stream.match('y')
        return
    else:
        raise SyntaxError('unexpected symbol {}'.format(sym))

def parse():
    from inputstream import InputStream
    stream = InputStream() # reads from stdin
    try:
        exp(stream)
        if stream.end_of_file():
            print("parse successful")
        else:
            raise SyntaxError("bad syntax at {}".format(stream.pointer()))
    except Exception as e:
        print("error: " + str(e))

if __name__ == "__main__":
    parse()
