# Cuppa1 compiler driver with LLVM backend

import sys
from argparse import ArgumentParser
from cuppa1_fe import parse
from cuppa1_llvm_codegen import codegen
from dumpast import dumpast

def cc(input_stream,
       ast_switch=False,
       ir_switch=False,
       exception_switch=False):

    try:
        ast = parse(input_stream)
        if ast_switch:
            dumpast(ast)
            sys.exit()
        code = codegen(ast, ir_switch)
        return code
    except Exception as e:
        if exception_switch:
            raise e
        else:
            print('error: ' + str(e))
            sys.exit()

if __name__ == "__main__":
    # parse command line args
    aparser = ArgumentParser()
    aparser.add_argument('input', metavar='input_file', help='cuppa1 input file')
    aparser.add_argument('-ast', help='dump ast', action="store_true")
    aparser.add_argument('-e', help='full exception dump', action="store_true")
    aparser.add_argument('-ir', help='generate llvm ir code', action="store_true")
    aparser.add_argument('-o', metavar='output_file', help='llvm output file')

    args = vars(aparser.parse_args())

    if args['ast']:
        ast_switch = True
    else:
        ast_switch = False

    if args['e']:
        exception_switch = True
    else:
        exception_switch = False

    if args['ir']:
        ir_switch = True
    else:
        ir_switch = False

    f = open(args['input'], 'r')
    input_stream = f.read()
    f.close()

    # run the compiler
    code = cc(input_stream,
              ast_switch,
              ir_switch,
              exception_switch)

    if args['o']:
        f = open(args['o'], 'w')
        f.write(code)
        f.close()
    else:
        print(code)
