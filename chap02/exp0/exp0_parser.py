'''
sLL(1) grammar for Exp0 with lookahead sets:

    stmt_list : {p,s} stmt stmt_list
              | {""} ""

    stmt : {p} p exp ;
         | {s} s var exp ;

    exp : {+} + exp exp
        | {-} - exp exp
        | {()} ( exp )
        | {x,y,z} var
        | {0,1,2,3,4,5,6,7,8,9} num

    var : {x} x
        | {y} y
        | {z} z

    num : {0} 0
        | {1} 1
        | {2} 2
        | {3} 3
        | {4} 4
        | {5} 5
        | {6} 6
        | {7} 7
        | {8} 8
        | {9} 9

Example program: s x 1; p (+ x 1);
'''


def stmt_list(stream):
    sym = stream.pointer()
    if sym in ['p','s']:
        stmt(stream)
        stmt_list(stream)
        return
    else:
        return

def stmt(stream):
    sym = stream.pointer()
    if sym in ['p']:
        stream.match('p')
        exp(stream)
        stream.match(';')
        return
    elif sym in ['s']:
        stream.match('s')
        var(stream)
        exp(stream)
        stream.match(';')
        return
    else:
        raise SyntaxError('unexpected symbol {} while parsing'.format(sym))

def exp(stream):
    sym = stream.pointer()
    if sym in ['+']:
        stream.match('+')
        exp(stream)
        exp(stream)
        return
    elif sym in ['-']:
        stream.match('-')
        exp(stream)
        exp(stream)
        return
    elif sym in ['(']:
        stream.match('(')
        exp(stream)
        stream.match(')')
        return
    elif sym in ['x', 'y', 'z']:
        var(stream)
        return
    elif sym in ['0', '1', '2', '3', '4', '5', '6','7', '8', '9']:
        num(stream)
        return
    else:
        raise SyntaxError('unexpected symbol {} while parsing'.format(sym))

def var(stream):
    sym = stream.pointer()
    if sym in ['x']:
        stream.match('x')
        return
    elif sym in ['y']:
        stream.match('y')
        return
    elif sym in ['z']:
        stream.match('z')
        return
    else:
        raise SyntaxError('unexpected symbol {} while parsing'.format(sym))

def num(stream):
    sym = stream.pointer()
    if sym in ['0']:
        stream.match('0')
        return
    elif sym in ['1']:
        stream.match('1')
        return
    elif sym in ['2']:
        stream.match('2')
        return
    elif sym in ['3']:
        stream.match('3')
        return
    elif sym in ['4']:
        stream.match('4')
        return
    elif sym in ['5']:
        stream.match('5')
        return
    elif sym in ['6']:
        stream.match('6')
        return
    elif sym in ['7']:
        stream.match('7')
        return
    elif sym in ['8']:
        stream.match('8')
        return
    elif sym in ['9']:
        stream.match('9')
        return
    else:
        raise SyntaxError('unexpected symbol {} while parsing'.format(sym))

def parse():
    from inputstream import InputStream
    stream = InputStream() # reads from stdin
    try:
        stmt_list(stream) # call the parser function for start symbol
        if stream.end_of_file():
            print("parse successful")
        else:
            raise SyntaxError("bad syntax at {}".format(stream.pointer()))
    except Exception as e:
        print("error: " + str(e))

if __name__ == "__main__":
    parse()
