# Cuppa1 compiler

from argparse import ArgumentParser
from cuppa1_fe import parse
from cuppa1_codegen import walk as codegen
from cuppa1_fold import walk as fold
from cuppa1_output import output
from cuppa1_output import peephole_opt

def cc(input_stream, opt = False):
    try:
        ast = parse(input_stream)
        if opt:
            ast = fold(ast) # constant fold optimizer
        instr_stream = codegen(ast) + [('stop',)]
        if opt:
            peephole_opt(instr_stream) # peephole optimizer
        bytecode = output(instr_stream)
        return bytecode
    except Exception as e:
        print('error: ' + str(e))
        return None

if __name__ == "__main__":
    # parse command line args
    aparser = ArgumentParser()
    aparser.add_argument('-O', action='store_true', help='optimization flag')
    aparser.add_argument('input', metavar='input_file', help='cuppa1 input file')
    aparser.add_argument('-o', metavar='output_file', help='exp1bytecode output file')

    args = vars(aparser.parse_args())

    f = open(args['input'], 'r')
    input_stream = f.read()
    f.close()

    # run the compiler
    bytecode = cc(input_stream=input_stream, opt=args['O'])

    if not args['o']:
        print(bytecode)
    else:
        f = open(args['o'], 'w')
        f.write(bytecode)
        f.close()
