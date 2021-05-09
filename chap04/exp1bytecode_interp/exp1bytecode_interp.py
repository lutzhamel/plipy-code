#!/usr/bin/env python

from exp1bytecode_interp_fe import parse
from exp1bytecode_interp_state import state

#####################################################################################
def interp_program():
    'execute abstract bytecode machine'

    state.instr_ix = 0 # start at the first instruction

    # keep interpreting until we run out of instructions
    # or we hit a 'stop'
    while True:
        if state.instr_ix == len(state.program):
            break  # no more instructions
        else:
            instr = state.program[state.instr_ix] # fetch instr

        # instruction format: (type, [arg1, arg2, ...])
        type = instr[0]

        # interpret instruction
        if type == 'PRINT':
            # PRINT exp
            exp_tree = instr[1]
            val = eval_exp_tree(exp_tree)
            print("{}".format(val))
            state.instr_ix += 1

        elif type == 'STORE':
            # STORE var exp
            var_name = instr[1]
            val = eval_exp_tree(instr[2])
            state.symbol_table[var_name] = val
            state.instr_ix += 1

        elif type == 'INPUT':
            # INPUT var
            var_name = instr[1]
            val = input("Please enter a value for {}: ".format(var_name))
            state.symbol_table[var_name] = int(val)
            state.instr_ix += 1

        elif type == 'JUMPT':
            # JUMPT exp label
            val = eval_exp_tree(instr[1])
            if val:
                state.instr_ix = state.label_table[instr[2]]
            else:
                state.instr_ix += 1

        elif type == 'JUMPF':
            # JUMPF exp label
            val = eval_exp_tree(instr[1])
            if not val:
                state.instr_ix = state.label_table[instr[2]]
            else:
                state.instr_ix += 1

        elif type == 'JUMP':
            # JUMP label
            state.instr_ix = state.label_table[instr[1]]

        elif type == 'STOP':
            # STOP
            break

        elif type == 'NOOP':
            # NOOP
            state.instr_ix += 1

        else:
            raise ValueError("Unexpected instruction: {}"
                             .format(type))


#####################################################################################
def eval_exp_tree(node):
    'walk expression tree and evaluate to an integer value'

    # tree nodes are tuples (TYPE, [arg1, arg2,...])
    type = node[0]

    if type == 'ADD':
        # ADD exp exp
        v_left = eval_exp_tree(node[1])
        v_right = eval_exp_tree(node[2])
        return v_left + v_right

    elif type == 'SUB':
        # SUB exp exp
        v_left = eval_exp_tree(node[1])
        v_right = eval_exp_tree(node[2])
        return v_left - v_right

    elif type == 'MUL':
        # MUL exp exp
        v_left = eval_exp_tree(node[1])
        v_right = eval_exp_tree(node[2])
        return v_left * v_right

    elif type == 'DIV':
        # DIV exp exp
        v_left = eval_exp_tree(node[1])
        v_right = eval_exp_tree(node[2])
        return v_left // v_right # integer division!

    elif type == 'EQ':
        # EQ exp exp
        v_left = eval_exp_tree(node[1])
        v_right = eval_exp_tree(node[2])
        return 1 if v_left == v_right else 0

    elif type == 'LE':
        # LE exp exp
        v_left = eval_exp_tree(node[1])
        v_right = eval_exp_tree(node[2])
        return 1 if v_left <= v_right else 0

    elif type == 'UMINUS':
        # UMINUS exp
        val = eval_exp_tree(node[1])
        return - val

    elif type == 'NOT':
        # NOT exp
        val = eval_exp_tree(node[1])
        return 0 if val != 0 else 1

    elif type == 'NAME':
        # NAME var_name
        return state.symbol_table.get(node[1],0)

    elif type == 'NUMBER':
        # NUMBER val
        return int(node[1])

    else:
        raise ValueError("Unexpected node type: {}"
                         .format(type))

#####################################################################################
def interp(input_stream):
    'driver for our Exp1bytecode interpreter.'

    try:
        state.initialize()  # initialize our abstract machine
        parse(input_stream) # build the IR
        interp_program()    # interpret the IR
    except Exception as e:
        print("error: "+str(e))

#####################################################################################
if __name__ == '__main__':
    import sys
    import os

    if len(sys.argv) == 1: # no args - read stdin
        char_stream = sys.stdin.read()
    else: # last arg is filename to open and read
        input_file = sys.argv[-1]
        if not os.path.isfile(input_file):
            print("unknown file {}".format(input_file))
            sys.exit(0)
        else:
            f = open(input_file, 'r')
            char_stream = f.read()
            f.close()

    interp(char_stream)
