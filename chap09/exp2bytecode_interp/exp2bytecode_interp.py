#!/usr/bin/env python3

from argparse import ArgumentParser
from exp2bytecode_fe import parse
from exp2bytecode_interp_state import state
from pprint import pprint

#####################################################################################
def get_tsx():
    # compute the 'top of stack' index
    return len(state.runtime_stack) - 1

#####################################################################################
def store_storable(storable, val):
    # store the value in the appropriate storable
    if storable[0] == 'ID':
        # ('ID', name)
        name = storable[1]
        state.symbol_table[name] = val

    elif storable[0] == 'RVX':
        # ('RVX',)
        state.rvx = val

    elif storable[0] == 'TSX':
        # ('TSX', opt_offset_exp)
        tsx = get_tsx()
        if storable[1]:
            offset = eval_exp_tree(storable[1])
            state.runtime_stack[tsx+offset] = val
        else:
            state.runtime_stack[tsx] = val

    else:
        raise ValueError("Unknown storable {}".format(storable[0]))

#####################################################################################
def interp_program():
    'execute abstract bytecode machine'

    # We cannot use the list iterator here because we
    # need to be able to interpret jump instructions

    # start at the first instruction in program
    state.instr_ix = 0

    # keep interpreting until we run out of instructions
    # or we hit a 'stop'
    while True:
        if state.instr_ix == len(state.program):
            # no more instructions
            break
        else:
            # get instruction from program
            instr = state.program[state.instr_ix]

        # instruction format: (type, [arg1, arg2, ...])
        type = instr[0]

        # interpret instruction
        if type == 'PRINT':
            # PRINT string? exp
            val = eval_exp_tree(instr[2])
            str = instr[1] if instr[1] else ""
            print("{}{}".format(str, val))
            state.instr_ix += 1

        elif type == 'INPUT':
            # INPUT string? storable
            storable = instr[2]
            str = instr[1] if instr[1] else "Please enter a value: "
            val = int(input(str))
            store_storable(storable, val)
            state.instr_ix += 1

        elif type == 'STORE':
            # STORE storable exp
            storable = instr[1]
            exp = instr[2]
            val = eval_exp_tree(exp)
            store_storable(storable, val)
            state.instr_ix += 1

        elif type == 'CALL':
            # CALL label
            # push the return address onto the stack
            state.runtime_stack.append(state.instr_ix+1)
            # get the target address from the label table
            label = instr[1]
            state.instr_ix = state.label_table.get(label)

        elif type == 'RETURN':
            # RETURN
            # pop the return address off the stack and jump to it
            state.instr_ix = state.runtime_stack.pop()

        elif type == 'PUSHV':
            # PUSHV exp
            exp_tree = instr[1]
            val = eval_exp_tree(exp_tree)
            # push value onto stack
            state.runtime_stack.append(val)
            state.instr_ix += 1

        elif type == 'POPV':
            # POPV storable?
            storable = instr[1]
            val = state.runtime_stack.pop()
            if storable:
                store_storable(storable, val)
            state.instr_ix += 1

        elif type == 'PUSHF':
            # PUSHF size_exp
            size_val = eval_exp_tree(instr[1])
            # pushing a stack frame onto the stack
            # zeroing out each stack location in the frame
            for i in range(size_val):
                state.runtime_stack.append(0)
            state.instr_ix += 1

        elif type == 'POPF':
            # POPF size_exp
            size_val = eval_exp_tree(instr[1])
            # popping a stack frame off the stack
            for i in range(size_val):
                state.runtime_stack.pop()
            state.instr_ix += 1

        elif type == 'JUMPT':
            # JUMPT exp label
            val = eval_exp_tree(instr[1])
            if val:
                state.instr_ix = state.label_table.get(instr[2])
            else:
                state.instr_ix += 1

        elif type == 'JUMPF':
            # JUMPF exp label
            val = eval_exp_tree(instr[1])
            if not val:
                state.instr_ix = state.label_table.get(instr[2])
            else:
                state.instr_ix += 1

        elif type == 'JUMP':
            # JUMP label
            state.instr_ix = state.label_table.get(instr[1], None)

        elif type == 'STOP':
            # STOP
            break

        elif type == 'NOOP':
            # NOOP
            state.instr_ix += 1

        else:
            raise ValueError("Unexpected instruction type: {}".format(p[1]))

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
        return v_left // v_right

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
        # 'UMINUS' exp
        val = eval_exp_tree(node[1])
        return - val

    elif type == 'NOT':
        # NOT exp
        val = eval_exp_tree(node[1])
        return 0 if val != 0 else 1

    elif type == 'ID':
        # ID var_name
        return state.symbol_table.get(node[1],0)

    elif type == 'RVX':
        # RVX
        return state.rvx

    elif type == 'TSX':
        # TSX opt_offset
        tsx = get_tsx()
        offset_exp = node[1]
        if offset_exp:
            val = eval_exp_tree(offset_exp)
            return state.runtime_stack[tsx+val]
        else:
            return state.runtime_stack[tsx]

    elif type == 'NUMBER':
        # NUMBER val
        return int(node[1])

    else:
        raise ValueError("Unexpected expression type: {}".format(type))

#####################################################################################
def interp(input_stream):
    'driver for our Exp2bytecode interpreter.'
    # initialize our abstract machine
    state.initialize()
    # build the IR
    parse(input_stream)
    # interpret the IR
    interp_program()

#####################################################################################
if __name__ == '__main__':
    # parse command line args
    aparser = ArgumentParser()
    aparser.add_argument('input')

    args = vars(aparser.parse_args())

    f = open(args['input'], 'r')
    input_stream = f.read()
    f.close()

    interp(input_stream=input_stream)
