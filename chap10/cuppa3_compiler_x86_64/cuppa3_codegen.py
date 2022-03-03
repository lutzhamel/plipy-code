'''
codegen: this is the code generator for our Cuppa3 compiler

NOTE: this code generator does not need access to the symbol table,
      the abstraction level of the AST has been lowered already to the level
      of the machine code

we map all integers into 8 byte words on the target machine.
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
        code += [('push', eloc)]
    return code

#########################################################################
def pop_args(args):

    if args[0] != 'LIST':
        raise ValueError("expected an argument list")

    ll = args[1]
    nitems = len(ll)
    nbytes = nitems*8
    code = [('add', '$'+str(nbytes), '%rsp')]
    return code

#########################################################################
def init_formal_args(formal_args):
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
               local var 1     <- %rsp

    The local vars include the formal parameters. Here the frame size is m.
    '''
    global curr_frame_size

    if formal_args[0] != 'LIST':
        raise ValueError("expected an argument list")

    ll = formal_args[1]
    code = list()
    arg_ix = 0

    for id in ll:
        (ADDR, sym) = id
        # the last term in the following expression is the size of
        # the return address.
        offset = str(arg_ix*8 + curr_frame_size*8 + 1*8)
        code += [('mov', str(offset)+'(%rsp)', '%eax')]
        code += [('mov', '%eax', sym)]
        arg_ix += 1

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

    code += [('jmp', ignore_label)]
    code += [('#','####################################')]
    code += [('#','Start Function ' + name)]
    code += [('#','####################################')]
    code += [(name + ':',)]
    code += [('sub', '$'+str(curr_frame_size*8), '%rsp')]
    code += init_formal_args(formal_arglist)
    code += walk(body)
    code += [('add', '$'+str(curr_frame_size*8), '%rsp')]
    code += [('ret',)]
    code += [('#','####################################')]
    code += [('#','End Function ' + name)]
    code += [('#','####################################')]
    code += [(ignore_label + ':',)]
    code += [('nop',)]

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
        code += [('mov', eloc, '%eax')]

    code += [('add', '$'+str(curr_frame_size*8), '%rsp')]
    code += [('ret',)]

    return code

#########################################################################
def assign_stmt(node):

    (ASSIGN, (ADDR, target), exp) = node

    (ecode, eloc) = walk(exp)
    code = list()

    code += ecode
    code += [('mov', eloc, '%eax')]
    code += [('mov', '%eax', target)]

    return code

#########################################################################
def get_stmt(node):

    (GET, (ADDR, target)) = node

    code = list()
    code += [('call', 'get')]
    code += [('mov', '%eax', target)]

    return code

#########################################################################
def put_stmt(node):

    (PUT, exp) = node

    (ecode, eloc) = walk(exp)
    code = list()

    code += ecode
    code += [('push', eloc)]
    code += [('call', 'put')]
    code += [('add', '$8', '%rsp')]

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
    code += [('mov', '$0', '%eax')]
    code += [('cmp', cond_loc, '%eax')]
    code += [('je', bottom_label)]
    code += body_code
    code += [('jmp', top_label)]
    code += [(bottom_label + ':',)]
    code += [('nop',)]

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
        code += [('mov', '$0', '%eax')]
        code += [('cmp', cond_loc, '%eax')]
        code += [('je', end_label)]
        code += s1_code
        code += [(end_label + ':',)]
        code += [('nop',)]

        return code

    else:
        else_label = label()
        end_label = label()
        (cond_code, cond_loc) = walk(cond)
        s1_code = walk(s1)
        s2_code = walk(s2)
        code = list()

        code += cond_code
        code += [('mov', '$0', '%eax')]
        code += [('cmp', cond_loc, '%eax')]
        code += [('je', else_label)]
        code += s1_code
        code += [('jmp', end_label)]
        code += [(else_label + ':',)]
        code += s2_code
        code += [(end_label + ':',)]
        code += [('nop',)]

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

    if OP not in ['PLUS', 'MINUS', 'MUL', 'DIV', 'EQ', 'LE']:
        raise ValueError('pattern match failed on ' + OP)

    if OP == 'PLUS':
        INSTR = 'add'
    elif OP == 'MINUS':
        INSTR = 'sub'
    elif OP == 'MUL':
        INSTR = 'imul'
    elif OP == 'DIV':
        INSTR = 'idiv'
    elif OP == 'EQ':
        INSTR = 'jne'
    elif OP == 'LE':
        INSTR = 'jg'

    (lcode, lloc) = walk(c1)
    (rcode, rloc) = walk(c2)
    code = list()

    if OP in ['PLUS', 'MINUS', 'MUL', 'DIV']:
        code += lcode
        code += rcode
        code += [('mov', lloc, '%eax')]
        code += [('mov', rloc, '%ebx')]
        code += [(INSTR, '%ebx', '%eax')]
        code += [('mov', '%eax', target)]
    elif OP in ['EQ', 'LE']:
        # relational operators are a bit complicated - we keep
        # the results in variables...therefore we have the explicit
        # test and store code
        else_label = label();
        end_label = label();
        code += lcode
        code += rcode
        code += [('mov', lloc, '%eax')]
        code += [('mov', rloc, '%ebx')]
        code += [('cmp', '%ebx', '%eax')]
        code += [(INSTR, else_label)]
        code += [('mov', '$1', '%eax')]
        code += [('jmp', end_label)]
        code += [(else_label+':',)]
        code += [('mov', '$0', '%eax')]
        code += [(end_label+':',)]
        code += [('mov', '%eax', target)]
    else:
        raise ValueError("unknow operator {}".format(OP))

    return (code, target)

#########################################################################
def call_exp(node):

    (CALLEXP, (ADDR0, target), (ADDR1, name), actual_args) = node

    code = list()
    code += push_args(actual_args)
    code += [('call', name)]
    code += pop_args(actual_args)
    code += [('mov', '%eax', target)]

    return (code, target)

#########################################################################
def integer_exp(node):

    (INTEGER, value) = node

    code = list()
    loc = '$' + str(value)

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
    code += [('mov', eloc, '%eax')]
    code += [('neg', '%eax')]
    code += [('mov', '%eax', target)]

    return (code, target)

#########################################################################
def not_exp(node):

    (NOT, (ADDR, target), e) = node

    (ecode, eloc) = walk(e)

    code = list()
    code += ecode
    code += [('mov', '$0', '%eax')]
    code += [('cmp', eloc, '%eax')]
    code += [('sete', '%al')]
    code += [('mov', '%eax', target)]

    return (code, target)

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
