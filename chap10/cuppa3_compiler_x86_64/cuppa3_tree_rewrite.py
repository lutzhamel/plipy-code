'''
a tree walker to rewrite Cuppa3 AST into a form that is
easily used to generate code for low level machines.

just as in previous compilers we do not use the symbol symbol_table
table to hold values but to hold (name, target_name) pairs.

we map all integers into 8 byte words on the target machine.
'''

from cuppa3_symtab import symtab

#########################################################################
_temp_cnt = 0

def make_temp_name():
    global _temp_cnt
    new_name = "v$" + str(_temp_cnt)
    _temp_cnt += 1
    return new_name

#########################################################################
def declare_temp():
    name = make_temp_name()
    target_name = symtab.make_target_name()
    symtab.declare(name, ('INTEGER', target_name))
    if not symtab.in_function:
        symtab.global_vars += [(target_name, 8)]
    return target_name

#######################################################################
def eval_actual_args(args):
    '''
    Walk the list of actual arguments, evaluate them, and
    return a list with the evaluated actual values
    '''
    (LIST, ll) = args

    outlist = []
    for e in ll:
        t = walk(e)
        outlist.append(t)
    return ('LIST', outlist)

#########################################################################
def declare_formal_args(formal_args):

    (LIST, fl) = formal_args

    outlist = list()
    for (ID, sym) in fl:
        target_name = symtab.make_target_name()
        symtab.declare(sym, ('INTEGER', target_name))
        outlist.append(('ADDR', target_name))
    return ('LIST', outlist)

#########################################################################
def handle_call(call_kind, name, actual_arglist):

    val = symtab.lookup_sym(name)

    if val[0] != 'FUNVAL':
        raise ValueError("expected a function value.")

    # unpack the funval tuple
    (FUNVAL, formal_arglist) = val

    if len(formal_arglist) != len(actual_arglist):
        raise ValueError("function {} expects {} arguments"
                         .format(name, len(formal_arglist)))

    # convert the actual values into three-address codes
    actual_val_args = eval_actual_args(actual_arglist)

    if call_kind == 'CALLEXP':
        return ('CALLEXP',
                ('ADDR', declare_temp()),
                ('ADDR', name),
                actual_val_args)
    else:
        return ('CALLSTMT', ('ADDR', name), actual_val_args)

#########################################################################
# node functions
#########################################################################
def stmtlist(node):

    (STMTLIST, lst) = node

    outlist = list()
    for stmt in lst:
        outlist.append(walk(stmt))

    return ('STMTLIST', outlist)

#########################################################################
def nil(node):

    (NIL,) = node

    return ('NIL',)

#########################################################################
# Note: We are walking the body of a function declaration to figure out
# how many local variables there are. We need this information in order
# to compute the frame size of the function. Also, we need to replace
# original function local variables with their stack frame target names.
def fundecl_stmt(node):

    (FUNDECL, (ID, name), arglist, body) = node

    # we don't need the function body - abbreviated function value
    funval = ('FUNVAL', arglist)
    symtab.declare(name, funval)

    symtab.enter_function()
    new_arglist = declare_formal_args(arglist)
    new_body = walk(body)
    frame_size = symtab.get_frame_size()
    symtab.exit_function()

    return ('FUNDEF',
            ('ADDR', name),
            new_arglist,
            new_body,
            ('FRAMESIZE', frame_size))

#########################################################################
def vardecl_stmt(node):

    (VARDECL, (ID, name), init_val) = node

    t = walk(init_val)
    target_name = symtab.make_target_name()
    symtab.declare(name, ('INTEGER', target_name))
    if not symtab.in_function:
        symtab.global_vars += [(target_name, 8)]

    return ('ASSIGN', ('ADDR', target_name), t)

#########################################################################
def assign_stmt(node):

    (ASSIGN, (ID, name), exp) = node

    t = walk(exp)
    target_name = symtab.get_target_name(name)
    return ('ASSIGN', ('ADDR', target_name), t)

#########################################################################
def get_stmt(node):

    (GET, (ID, name)) = node

    target_name = symtab.get_target_name(name)
    return ('GET', ('ADDR', target_name))

#########################################################################
def put_stmt(node):

    (PUT, exp) = node

    t = walk(exp)

    return ('PUT', t)

#########################################################################
def call_stmt(node):

    (CALLSTMT, (ID, name), actual_args) = node

    return handle_call('CALLSTMT', name, actual_args)

#########################################################################
def return_stmt(node):

    (RETURN, exp) = node

    if not symtab.in_function:
        raise ValueError("return has to appear in a function context.")

    t = walk(exp)

    return ('RETURN', t)

#########################################################################
def while_stmt(node):

    (WHILE, cond, body) = node

    t1 = walk(cond)
    t2 = walk(body)

    return ('WHILE', t1, t2)

#########################################################################
def if_stmt(node):

    (IF, cond, then_stmt, else_stmt) = node

    t1 = walk(cond)
    t2 = walk(then_stmt)
    t3 = walk(else_stmt)
    return ('IF', t1, t2, t3)

#########################################################################
def block_stmt(node):

    (BLOCK, stmt_list) = node

    symtab.push_scope()
    t = walk(stmt_list)
    symtab.pop_scope()

    return ('BLOCK', t)

#########################################################################
def binop_exp(node):
    # turn expressions into three-address codes

    (OP, c1, c2) = node

    t1 = walk(c1)
    t2 = walk(c2)

    target_name = declare_temp()

    return (OP, ('ADDR', target_name), t1, t2)

#########################################################################
def integer_exp(node):

    (INTEGER, value) = node

    return ('INTEGER', value)

#########################################################################
def id_exp(node):

    (ID, name) = node

    target_name = symtab.get_target_name(name)

    return ('ADDR', target_name)

#########################################################################
def call_exp(node):

    (CALLEXP, (ID, name), actual_args) = node

    return handle_call('CALLEXP', name, actual_args)

#########################################################################
def uminus_exp(node):

    (UMINUS, exp) = node

    t = walk(exp)
    target_name = declare_temp()

    return ('UMINUS', ('ADDR', target_name), t)

#########################################################################
def not_exp(node):

    (NOT, exp) = node

    t = walk(exp)
    target_name = declare_temp()

    return ('NOT', ('ADDR', target_name), t)

#########################################################################
def paren_exp(node):

    (PAREN, exp) = node

    # get rid of parenthesis - not necessary in AST
    return walk(exp)

#########################################################################
# walk
#########################################################################
def walk(node):
    # node format: (TYPE, [child1[, child2[, ...]]])
    type = node[0]

    if type in dispatch:
        node_function = dispatch[type]
        return node_function(node)
    else:
        raise ValueError("walk: unknown tree node type: " + type)

# a dictionary to associate tree nodes with node functions
dispatch = {
    'STMTLIST': stmtlist,
    'NIL'     : nil,
    'FUNDECL' : fundecl_stmt,
    'VARDECL' : vardecl_stmt,
    'ASSIGN'  : assign_stmt,
    'GET'     : get_stmt,
    'PUT'     : put_stmt,
    'CALLSTMT': call_stmt,
    'RETURN'  : return_stmt,
    'WHILE'   : while_stmt,
    'IF'      : if_stmt,
    'BLOCK'   : block_stmt,
    'INTEGER' : integer_exp,
    'ID'      : id_exp,
    'CALLEXP' : call_exp,
    'PAREN'   : paren_exp,
    'PLUS'    : binop_exp,
    'MINUS'   : binop_exp,
    'MUL'     : binop_exp,
    'DIV'     : binop_exp,
    'EQ'      : binop_exp,
    'LE'      : binop_exp,
    'UMINUS'  : uminus_exp,
    'NOT'     : not_exp
}
