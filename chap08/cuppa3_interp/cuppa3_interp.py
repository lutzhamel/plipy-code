#!/usr/bin/env python
# Cuppa3 interpreter

from cuppa3_fe import parse
from cuppa3_symtab import symtab
from cuppa3_interp_walk import walk
from dumpast import dumpast

def interp(input_stream, dump=False, exceptions=False):
    try:
        symtab.initialize()
        ast = parse(input_stream)
        if dump:
            dumpast(ast)
        else:
            walk(ast)
    except Exception as e:
        if exceptions:
            raise e # rethrow for visibility
        else:
            print("error: "+str(e))
    return None

if __name__ == "__main__":
    import sys
    import os

    ast_switch = False
    char_stream = ''

    if len(sys.argv) == 1: # no args - read stdin
        char_stream = sys.stdin.read()
    else:
        # test if there is a switch as first arg
        ast_switch = sys.argv[1] == '-d'
        except_switch = sys.argv[1] == '-e'
        # last arg is the filename to open and read
        input_file = sys.argv[-1]
        if not os.path.isfile(input_file):
            print("unknown file {}".format(input_file))
            sys.exit(0)
        else:
            f = open(input_file, 'r')
            char_stream = f.read()
            f.close()

    interp(char_stream, dump=ast_switch, exceptions=except_switch)
