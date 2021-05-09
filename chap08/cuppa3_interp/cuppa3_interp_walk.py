# A tree walker to interpret Cuppa3 programs

from cuppa3_symtab import symtab
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
    assert_match(LIST, 'LIST')

    outlist = []
    for e in ll:
        v = walk(e)
        outlist.append(('INTEGER', v))

    return ('LIST', outlist)

#########################################################################
def declare_formal_args(formal_args, actual_val_args):
    '''
    Walk the formal argument list and declare the identifiers on that
    list using the corresponding actual args as initial values.
    NOTE: this is where we implement by-value argument passing
    '''
    (LIST, fl) = formal_args
    assert_match(LIST, 'LIST')
    (LIST, avl) = actual_val_args
    assert_match(LIST, 'LIST')

    if len(fl) != len(avl):
        raise ValueError("actual and formal argument lists do not match")

    for ((ID, f), v) in zip(fl, avl):
        symtab.declare(f, v)

#########################################################################
def handle_call(name, actual_arglist):
    '''
    handle calls for both call statements and call expressions.
    '''

    val = symtab.lookup_sym(name)

    if val[0] != 'FUNVAL':
        raise ValueError("{} is not a function".format(name))

    # unpack the funval tuple
    (FUNVAL, formal_arglist, body, context) = val

    # set up the environment for static scoping and then execute the function
    actual_val_args = eval_actual_args(actual_arglist)
    save_symtab = symtab.get_config()
    symtab.set_config(context)
    symtab.push_scope()
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
    assert_match(STMTLIST, 'STMTLIST')

    for stmt in lst:
        walk(stmt)

    return None

#########################################################################
def nil(node):

    (NIL,) = node
    assert_match(NIL, 'NIL')

    # do nothing!
    return None

#########################################################################
def fundecl_stmt(node):

    (FUNDECL, (ID, name), arglist, body) = node
    assert_match(FUNDECL, 'FUNDECL')
    assert_match(ID, 'ID')

    context = symtab.get_config()
    funval = ('FUNVAL', arglist, body, context)
    symtab.declare(name, funval)
    return None

#########################################################################
def vardecl_stmt(node):

    (VARDECL, (ID, name), init_val) = node
    assert_match(VARDECL, 'VARDECL')
    assert_match(ID, 'ID')

    value = walk(init_val)
    symtab.declare(name, ('INTEGER', value))
    return None

#########################################################################
def assign_stmt(node):

    (ASSIGN, (ID, name), exp) = node
    assert_match(ASSIGN, 'ASSIGN')
    assert_match(ID, 'ID')

    value = walk(exp)
    symtab.update_sym(name, ('INTEGER', value))

    return None

#########################################################################
def get_stmt(node):

    (GET, (ID, name)) = node
    assert_match(GET, 'GET')
    assert_match(ID, 'ID')

    s = input("Value for " + name + '? ')

    try:
        value = int(s)
    except ValueError:
        raise ValueError("expected an integer value for " + name)

    symtab.update_sym(name, ('INTEGER', value))

    return None

#########################################################################
def put_stmt(node):

    (PUT, exp) = node
    assert_match(PUT, 'PUT')

    value = walk(exp)
    print("{}".format(value))

    return None

#########################################################################
def call_stmt(node):

    (CALLSTMT, (ID, name), actual_args) = node
    assert_match(CALLSTMT, 'CALLSTMT')
    assert_match(ID, 'ID')

    handle_call(name, actual_args)

    return None

#########################################################################
def return_stmt(node):

    (RETURN, exp) = node
    assert_match(RETURN, 'RETURN')

    value = walk(exp)
    raise ReturnValue(value)

#########################################################################
def while_stmt(node):

    (WHILE, cond, body) = node
    assert_match(WHILE, 'WHILE')

    while walk(cond) != 0:
        walk(body)

    return None

#########################################################################
def if_stmt(node):

        (IF, cond, then_stmt, else_stmt) = node
        assert_match(IF, 'IF')

        if walk(cond) != 0:
            walk(then_stmt)
        else:
            walk(else_stmt)
        return None

#########################################################################
def block_stmt(node):

    (BLOCK, stmt_list) = node
    assert_match(BLOCK, 'BLOCK')

    symtab.push_scope()
    walk(stmt_list)
    symtab.pop_scope()
    return None

#########################################################################
def plus_exp(node):

    (PLUS,c1,c2) = node
    assert_match(PLUS, 'PLUS')

    v1 = walk(c1)
    v2 = walk(c2)

    return v1 + v2

#########################################################################
def minus_exp(node):

    (MINUS,c1,c2) = node
    assert_match(MINUS, 'MINUS')

    v1 = walk(c1)
    v2 = walk(c2)

    return v1 - v2

#########################################################################
def mul_exp(node):

    (MUL,c1,c2) = node
    assert_match(MUL, 'MUL')

    v1 = walk(c1)
    v2 = walk(c2)

    return v1 * v2

#########################################################################
def div_exp(node):

    (DIV,c1,c2) = node
    assert_match(DIV, 'DIV')

    v1 = walk(c1)
    v2 = walk(c2)

    return v1 // v2

#########################################################################
def eq_exp(node):

    (EQ,c1,c2) = node
    assert_match(EQ, 'EQ')

    v1 = walk(c1)
    v2 = walk(c2)

    return 1 if v1 == v2 else 0

#########################################################################
def le_exp(node):

    (LE,c1,c2) = node
    assert_match(LE, 'LE')

    v1 = walk(c1)
    v2 = walk(c2)

    return 1 if v1 <= v2 else 0

#########################################################################
def integer_exp(node):

    (INTEGER, value) = node
    assert_match(INTEGER, 'INTEGER')

    return value

#########################################################################
def id_exp(node):

    (ID, name) = node
    assert_match(ID, 'ID')

    val = symtab.lookup_sym(name)

    if val[0] != 'INTEGER':
        raise ValueError("{} is not an integer".format(name))

    return val[1]

#########################################################################
def call_exp(node):

    (CALLEXP, (ID, name), actual_args) = node
    assert_match(CALLEXP, 'CALLEXP')
    assert_match(ID, 'ID')

    return_value = handle_call(name, actual_args)

    if return_value is None:
        raise ValueError("No return value from function {}".format(name))

    return return_value

#########################################################################
def uminus_exp(node):

    (UMINUS, exp) = node
    assert_match(UMINUS, 'UMINUS')

    val = walk(exp)
    return - val

#########################################################################
def not_exp(node):

    (NOT, exp) = node
    assert_match(NOT, 'NOT')

    val = walk(exp)
    return 0 if val != 0 else 1

#########################################################################
def paren_exp(node):

    (PAREN, exp) = node
    assert_match(PAREN, 'paren')

    # return the value of the parenthesized expression
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
    'PLUS'    : plus_exp,
    'MINUS'   : minus_exp,
    'MUL'     : mul_exp,
    'DIV'     : div_exp,
    'EQ'      : eq_exp,
    'LE'      : le_exp,
    'UMINUS'  : uminus_exp,
    'NOT'     : not_exp
}
