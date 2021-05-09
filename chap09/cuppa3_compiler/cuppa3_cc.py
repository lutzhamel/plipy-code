# Cuppa3 compiler

from argparse import ArgumentParser
from cuppa3_fe import parse
from cuppa3_tree_rewrite import walk as rewrite
from cuppa3_codegen import walk as codegen
from cuppa3_output import output
from dumpast import dumpast
import pprint

pp = pprint.PrettyPrinter()

def cc(input_stream,
       ast_switch=False,
       three_address_switch=False,
       bytecode_switch=False):

    try:
        ast = parse(input_stream)
        if ast_switch:
            dumpast(ast)
            return ""
        ast = rewrite(ast)
        if three_address_switch:
            dumpast(ast)
            return ""
        instr_stream = codegen(ast) + [('stop',)]
        if bytecode_switch:
            pp.pprint(instr_stream)
            return ""
        bytecode = output(instr_stream)
        return bytecode
    except Exception as e:
        print('error: ' + str(e))
        raise e
        return None

if __name__ == "__main__":
    # parse command line args
    aparser = ArgumentParser()
    aparser.add_argument('input', metavar='input_file', help='cuppa1 input file')
    aparser.add_argument('-o', metavar='output_file', help='exp2bytecode output file')
    aparser.add_argument('-a', help='dump ast', action="store_true")
    aparser.add_argument('-t', help='dump three address code tree', action="store_true")
    aparser.add_argument('-l', help='dump bytecode list', action="store_true")

    args = vars(aparser.parse_args())

    f = open(args['input'], 'r')
    input_stream = f.read()
    f.close()

    if args['a']:
        ast_switch = True
    else:
        ast_switch = False

    if args['t']:
        three_address_switch = True
    else:
        three_address_switch = False

    if args['l']:
        bytecode_switch = True
    else:
        bytecode_switch = False

    # run the compiler
    bytecode = cc(input_stream,
                  ast_switch=ast_switch,
                  three_address_switch=three_address_switch,
                  bytecode_switch=bytecode_switch)

    if args['o']:
        f = open(args['o'], 'w')
        f.write(bytecode)
        f.close()
    else:
        print(bytecode)
