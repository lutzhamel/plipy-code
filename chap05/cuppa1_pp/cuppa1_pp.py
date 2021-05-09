# Cuppa1 pretty printer

from cuppa1_fe import parse
from cuppa1_state import state
from cuppa1_pp1_walk import walk as pp1_walk
from cuppa1_pp2_walk import walk as pp2_walk
from cuppa1_pp2_walk import init_indent_level

def pp(input_stream):

    try:
        state.initialize()
        init_indent_level()
        ast = parse(input_stream)
        pp1_walk(ast)
        code = pp2_walk(ast)
        print(code)
    except Exception as e:
        print("error: "+str(e))

if __name__ == "__main__":
    import sys
    import os

    char_stream = ''

    if len(sys.argv) == 1: # no args - read stdin
        char_stream = sys.stdin.read()
    else:
        # last arg is the filename to open and read
        input_file = sys.argv[-1]
        if not os.path.isfile(input_file):
            print("unknown file {}".format(input_file))
            sys.exit(0)
        else:
            f = open(input_file, 'r')
            char_stream = f.read()
            f.close()

    pp(char_stream)
