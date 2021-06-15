'''
codegen: this is the code generator for our Cuppa3 compiler

NOTE: this code generator does not need access to the symbol table,
      the abstraction level of the AST has been lowered already to the level
      of the abstract machine code
'''

#########################################################################
# curr_frame_size: we use this global variable to broadcast the frame
# size of the current function definition to all the statements within
# the function body -- the return statement needs this information in order
# to generate the proper pop frame instruction. Outside of a
# function definition this value is set to None
curr_frame_size = None

#########################################################################
def push_args(args):

    if args[0] != 'LIST':
        raise ValueError("expected an argument list")

    # reversing the arg list because we need to push
    # args in reverse order
    # NOTE: reverse is an in-place op in Python
    ll = args[1].copy()
    ll.reverse()
    code = list()
    for e in ll:
        (ecode, eloc) = walk(e)
        code += ecode
        code += [('pushv', eloc)]
    return code

#########################################################################
def pop_args(args):

    if args[0] != 'LIST':
        raise ValueError("expected an argument list")

    ll = args[1]
    code = list()
    for e in ll:
        code += [('popv',)]
    return code

#########################################################################
def init_formal_args(formal_args, frame_size):
    '''
    in order to understand this function recall that the stack
    in the called function after the frame has been pushed
    looks like this

               ...
               actual arg n
               actual arg n-1
               ...
               actual arg 1
               return address
               local var m
               local var m-1
               local var 1     <- tsx

    The local vars include the formal parameters. Here the frame size is m.
    In order to find the location of the first actual argument we have to s
    kip over the frame and the return address:

    first actual arg:  %tsx[0-m-1]
    second actual arg: %tsx[-1-m-1]
    ...
    nth actual arg:    %tsx[-(n-1)-m-1]
    '''

    if formal_args[0] != 'LIST':
        raise ValueError("expected an argument list")

    ll = formal_args[1]
    code = list()
    arg_ix = 0
    for id in ll:
        (ADDR, sym) = id
        if ADDR != 'ADDR':
            raise ValueError("Expected and address.")
        offset = str(arg_ix - frame_size - 1)
        code += [('store', sym, '%tsx['+offset+']')]
        arg_ix -= 1
    return code

#########################################################################
# node functions
#########################################################################
# Statements
#########################################################################
def stmtlist(node):

    (STMTLIST, lst) = node

    code = list()
    for stmt in lst:
        code += walk(stmt)

    return code


#########################################################################
def fundef_stmt(node):

    global curr_frame_size

    # unpack node
    (FUNDEF,
     (ADDR, name),
     formal_arglist,
     body,
     (FRAMESIZE, curr_frame_size)) = node

    ignore_label = label()
    code = list()

    code += [('jump', ignore_label)]
    code += [('#','####################################')]
    code += [('#','Start Function ' + name)]
    code += [('#','####################################')]
    code += [(name + ':',)]
    code += [('pushf', str(curr_frame_size))]
    code += init_formal_args(formal_arglist, curr_frame_size)
    code += walk(body)
    code += [('popf', str(curr_frame_size))]
    code += [('return',)]
    code += [('#','####################################')]
    code += [('#','End Function ' + name)]
    code += [('#','####################################')]
    code += [(ignore_label + ':',)]
    code += [('noop',)]

    curr_frame_size = None

    return code

#########################################################################
def call_stmt(node):

    (CALLSTMT, (ADDR, name), actual_args) = node

    code = list()

    code += push_args(actual_args)
    code += [('call', name)]
    code += pop_args(actual_args)

    return code

#########################################################################
def return_stmt(node):
    global curr_frame_size

    (RETURN, exp) = node

    code = list()

    # if return has a return value
    if exp[0] != 'NIL':
        (ecode, eloc) = walk(exp)
        code += ecode
        code += [('store', '%rvx', eloc)]

    code += [('popf', str(curr_frame_size))]
    code += [('return',)]

    return code

#########################################################################
def assign_stmt(node):

    (ASSIGN, (ADDR, target), exp) = node

    (ecode, eloc) = walk(exp)
    code = list()

    code += ecode
    code += [('store', target, eloc)]

    return code

#########################################################################
def get_stmt(node):

    (GET, (ADDR, target)) = node

    code = [('input', target)]

    return code

#########################################################################
def put_stmt(node):

    (PUT, exp) = node

    (ecode, eloc) = walk(exp)
    code = list()

    code += ecode
    code += [('print', eloc)]

    return code

#########################################################################
def while_stmt(node):

    (WHILE, cond, body) = node

    top_label = label()
    bottom_label = label()
    (cond_code, cond_loc) = walk(cond)
    body_code = walk(body)
    code = list()

    code += [(top_label + ':',)]
    code += cond_code
    code += [('jumpf', cond_loc, bottom_label)]
    code += body_code
    code += [('jump', top_label)]
    code += [(bottom_label + ':',)]
    code += [('noop',)]

    return code

#########################################################################
def if_stmt(node):

    (IF, cond, s1, s2) = node

    if s2[0] == 'NIL':
        end_label = label();
        (cond_code, cond_loc) = walk(cond)
        s1_code = walk(s1)
        code = list()

        code += cond_code
        code += [('jumpf', cond_loc, end_label)]
        code += s1_code
        code += [(end_label + ':',)]
        code += [('noop',)]
        return code

    else:
        else_label = label()
        end_label = label()
        (cond_code, cond_loc) = walk(cond)
        s1_code = walk(s1)
        s2_code = walk(s2)
        code = list()

        code += cond_code
        code += [('jumpf', cond_loc, else_label)]
        code += s1_code
        code += [('jump', end_label)]
        code += [(else_label + ':',)]
        code += s2_code
        code += [(end_label + ':',)]
        code += [('noop',)]
        return code

#########################################################################
def block_stmt(node):

    (BLOCK, s) = node

    code = walk(s)

    return code

#########################################################################
# Expressions
#########################################################################
def binop_exp(node):

    (OP, (ADDR, target), c1, c2) = node


    if OP == 'PLUS':
        OPSYM = '+'
    elif OP == 'MINUS':
        OPSYM = '-'
    elif OP == 'MUL':
        OPSYM = '*'
    elif OP == 'DIV':
        OPSYM = '/'
    elif OP == 'EQ':
        OPSYM = '=='
    elif OP == 'LE':
        OPSYM = '=<'
    else:
        raise ValueError('unknown operation: ' + OP)

    (lcode, lloc) = walk(c1)
    (rcode, rloc) = walk(c2)
    code = list()

    code += lcode
    code += rcode
    code += [('store', target, '(' + OPSYM + ' ' + lloc + ' ' + rloc + ')')]

    return (code, target)

#########################################################################
def call_exp(node):

    (CALLEXP, (ADDR, target), (ADDR, name), actual_args) = node

    code = list()
    code += push_args(actual_args)
    code += [('call', name)]
    code += pop_args(actual_args)
    code += [('store', target, '%rvx')]

    return (code, target)

#########################################################################
def integer_exp(node):

    (INTEGER, value) = node

    code = list()
    loc = str(value)

    return (code, loc)

#########################################################################
def addr_exp(node):

    (ADDR, loc) = node

    code = list()

    return (code, loc)

#########################################################################
def uminus_exp(node):

    (UMINUS, (ADDR, target), e) = node

    (ecode, eloc) = walk(e)

    code = list()
    code += ecode
    code += [('store', target, '-' + eloc)]
    loc = target

    return (code, loc)

#########################################################################
def not_exp(node):

    (NOT, (ADDR, target), e) = node

    (ecode, eloc) = walk(e)

    code = list()
    code += ecode
    code += [('store', target, '!' + eloc)]
    loc = target

    return (code, loc)

#########################################################################
# walk
#########################################################################
def walk(node):
    node_type = node[0]

    if node_type in dispatch_dict:
        node_function = dispatch_dict[node_type]
        return node_function(node)

    else:
        raise ValueError("walk: unknown tree node type: " + node_type)

# a dictionary to associate tree nodes with node functions
dispatch_dict = {
    'STMTLIST' : stmtlist,
    'FUNDEF'   : fundef_stmt,
    'CALLSTMT' : call_stmt,
    'RETURN'   : return_stmt,
    'ASSIGN'   : assign_stmt,
    'GET'      : get_stmt,
    'PUT'      : put_stmt,
    'WHILE'    : while_stmt,
    'IF'       : if_stmt,
    'BLOCK'    : block_stmt,
    'CALLEXP'  : call_exp,
    'INTEGER'  : integer_exp,
    'ADDR'     : addr_exp,
    'UMINUS'   : uminus_exp,
    'NOT'      : not_exp,
    'PLUS'     : binop_exp,
    'MINUS'    : binop_exp,
    'MUL'      : binop_exp,
    'DIV'      : binop_exp,
    'EQ'       : binop_exp,
    'LE'       : binop_exp,
}

#########################################################################
label_id = 0

def label():
    global label_id
    s =  'L' + str(label_id)
    label_id += 1
    return s

#########################################################################
