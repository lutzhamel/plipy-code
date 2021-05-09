# A tree walker to interpret Cuppa4 programs

from cuppa4_symtab import symtab
from cuppa4_types import coerce, promote
from assertmatch import assert_match

#########################################################################
# Use the exception mechanism to return values from function calls

class ReturnValue(Exception):

    def __init__(self, value):
        self.value = value

    def __str__(self):
        return(repr(self.value))

#########################################################################
def eval_actual_args(args):
    '''
    Walk the list of actual arguments, evaluate them, and
    return a list with the evaluated actual values
    '''
    (LIST, ll) = args
    outlist = []
    for e in ll:
        v = walk(e)
        outlist.append(v)

    return ('LIST', outlist)

#########################################################################
def declare_formal_args(formal_args, actual_val_args):
    '''
    Walk the formal argument list and declare the identifiers on that
    list using the corresponding actual args as initial values.
    NOTE: this is where we implement by-value argument passing
    NOTE: the type coercion implements subtype polymorphism for functions
    '''
    (LIST, fl) = formal_args
    (LIST, avl) = actual_val_args

    for ((FORMALARG,tf,(ID,fs)), (ta,va)) in zip(fl,avl):
        symtab.declare(fs, ('CONST', tf, ('VALUE', coerce(tf,ta)(va))))

#########################################################################
def handle_call(name, actual_arglist):
    '''
    handle calls for both call statements and call expressions.
    '''
    # unpack the funval and type tuples
    (FUNVAL, type, formal_arglist, body, context) = symtab.lookup_sym(name)
    (FUNCTION_TYPE, ret_type, arg_types) = type

    # set up the environment for static scoping and then execute the function
    actual_val_args = eval_actual_args(actual_arglist)
    save_symtab = symtab.get_config()
    symtab.set_config(context)
    symtab.push_scope(ret_type)
    declare_formal_args(formal_arglist, actual_val_args)

    # execute function
    return_value = None
    try:
        walk(body)
    except ReturnValue as val:
        return_value = val.value

    # NOTE: popping the function scope is not necessary because we
    # are restoring the original symtab configuration
    symtab.set_config(save_symtab)

    return return_value

#########################################################################
# node functions
#########################################################################
def stmtlist(node):

    (STMTLIST, lst) = node
    for stmt in lst:
        walk(stmt)
    return None

#########################################################################
def nil(node):

    (NIL,) = node
    return ('VOID_TYPE', None)

#########################################################################
def fundecl_stmt(node):

    (FUNDECL, (ID, name), type, arglist, body) = node

    context = symtab.get_config()
    funval = ('FUNVAL', type, arglist, body, context)
    symtab.declare(name, funval)

    return None

#########################################################################
def vardecl_stmt(node):

    (VARDECL, (ID, name), type, init_val) = node

    (ti, vi) = walk(init_val)
    symtab.declare(name, ('CONST', type, ('VALUE', coerce(type,ti)(vi))))

    return None

#########################################################################
def assign_stmt(node):

    (ASSIGN, (ID, name), exp) = node

    (t,v) = walk(exp)
    (CONST, ts, (VALUE, vs)) = symtab.lookup_sym(name)
    symtab.update_sym(name, ('CONST', t, ('VALUE', coerce(ts,t)(v))))

    return None

#########################################################################
def get_stmt(node):

    (GET, (ID, name)) = node
    (CONST, type, value) = symtab.lookup_sym(name)
    s = input("Value for " + name + '? ')
    try:
        # cannot use coerce here because that would be going
        # down the type hierarchy which is not supported
        if type[0] == 'STRING_TYPE':
            new_value = s
        elif type[0] == 'FLOAT_TYPE':
            new_value = float(s)
        elif type[0] == 'INTEGER_TYPE':
            new_value = int(s)
        else:
            raise ValueError("input not supported for this type")
    except ValueError:
        raise ValueError("expected a {} value for {}"
                .format(type[0], name))
    symtab.update_sym(name, ('CONST', type, ('VALUE', new_value)))
    return None

#########################################################################
def put_stmt(node):

    (PUT, exp) = node
    (type, value) = walk(exp)
    print("{}".format(value))
    return None

#########################################################################
def call_stmt(node):

    (CALLSTMT, (ID, name), actual_args) = node
    handle_call(name, actual_args)
    return None

#########################################################################
def return_stmt(node):

    (RETURN, exp) = node

    (t,v) = walk(exp)
    ret_type = symtab.lookup_ret_type()

    if ret_type == 'VOID_TYPE':
        raise ReturnValue(None)
    else:
        raise ReturnValue((ret_type, coerce(ret_type,t)(v)))

#########################################################################
def while_stmt(node):

    (WHILE, cond, body) = node

    while walk(cond)[1]:
        walk(body)

    return None

#########################################################################
def if_stmt(node):

    (IF, cond, then_stmt, else_stmt) = node

    if walk(cond)[1]:
        walk(then_stmt)
    else:
        walk(else_stmt)

    return None

#########################################################################
def block_stmt(node):

    (BLOCK, stmt_list) = node

    symtab.push_scope()
    walk(stmt_list)
    symtab.pop_scope()

    return None

#########################################################################
def plus_exp(node):

    (PLUS,c1,c2) = node

    (t1,v1) = walk(c1)
    (t2,v2) = walk(c2)

    t = promote(t1,t2)

    return (t, coerce(t,t1)(v1) + coerce(t,t2)(v2))

#########################################################################
def minus_exp(node):

    (MINUS,c1,c2) = node

    (t1,v1) = walk(c1)
    (t2,v2) = walk(c2)

    t = promote(t1,t2)

    return (t, coerce(t,t1)(v1) - coerce(t,t2)(v2))

#########################################################################
def mul_exp(node):

    (MUL,c1,c2) = node

    (t1,v1) = walk(c1)
    (t2,v2) = walk(c2)

    t = promote(t1,t2)

    return (t, coerce(t,t1)(v1) * coerce(t,t2)(v2))

#########################################################################
def div_exp(node):

    (DIV,c1,c2) = node

    (t1,v1) = walk(c1)
    (t2,v2) = walk(c2)

    t = promote(t1,t2)

    if t == 'INTEGER_TYPE':
        return ('INTEGER_TYPE', v1 // v2)
    else:
        return (t, coerce(t,t1)(v1) / coerce(t,t2)(v2))

#########################################################################
def eq_exp(node):

    (EQ,c1,c2) = node

    (t1,v1) = walk(c1)
    (t2,v2) = walk(c2)
    t = promote(t1, t2)

    if coerce(t,t1)(v1) == coerce(t,t2)(v2):
        return ('INTEGER_TYPE', 1)
    else:
        return ('INTEGER_TYPE', 0)

#########################################################################
def le_exp(node):

    (LE,c1,c2) = node

    (t1,v1) = walk(c1)
    (t2,v2) = walk(c2)
    t = promote(t1, t2)

    if coerce(t,t1)(v1) <= coerce(t,t2)(v2):
        return ('INTEGER_TYPE', 1)
    else:
        return ('INTEGER_TYPE', 0)

#########################################################################
def const_exp(node):

    (CONST, type, (VALUE, value)) = node
    return (type, value)

#########################################################################
def id_exp(node):

    (ID, name) = node
    (CONST, type, (VALUE, value)) = symtab.lookup_sym(name)

    return (type, value)

#########################################################################
def call_exp(node):

    (CALLEXP, (ID, name), actual_args) = node

    return_value = handle_call(name, actual_args)

    if not return_value:
        raise ValueError("No return value from function {}".format(name))
    else:
        return return_value

#########################################################################
def uminus_exp(node):

    (UMINUS, exp) = node
    (type, val) = walk(exp)

    return (type, - val)

#########################################################################
def not_exp(node):

    (NOT, exp) = node
    (type, val) = walk(exp)

    return ('INTEGER_TYPE', 0) if val else ('INTEGER_TYPE', 1)

#########################################################################
def paren_exp(node):

    (PAREN, exp) = node
    # return the (type,value) of the parenthesized expression
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
    'CONST'   : const_exp,
    'ID'      : id_exp,
    'CALLEXP' : call_exp,
    'PAREN'   : paren_exp,
    'PLUS'    : plus_exp,
    'MINUS'   : minus_exp,
    'MUL'     : mul_exp,
    'DIV'     : div_exp,
    'EQ'      : eq_exp,
    'LE'      : le_exp,
    'UMINUS'  : uminus_exp,
    'NOT'     : not_exp
}
