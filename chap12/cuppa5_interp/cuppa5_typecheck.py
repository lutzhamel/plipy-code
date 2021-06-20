# A tree walker to typecheck Cuppa5 programs

from cuppa5_symtab import symtab
from cuppa5_types import promote, safe_assign


#########################################################################
def declare_formal_args(formal_args):
    (LIST, fl) = formal_args

    for (FORMALARG, type, (ID, f)) in fl:
        symtab.declare(f, type)

#########################################################################
def check_call(function_type, actual_arguments):

    # unpack
    (FUNCTION_TYPE, ret_type, (LIST, formal_arg_types)) = function_type
    (LIST, actual_args_list) = actual_arguments

    # make sure arguments line up
    if len(formal_arg_types) != len(actual_args_list):
        raise ValueError("expected {} argument(s) got {}"
                    .format(len(formal_arg_types),
                            len(actual_args_list)))

    # type check association of actuals to formals
    for (tformal, a) in zip(formal_arg_types,actual_args_list):
        tactual = walk(a)
        if not safe_assign(tformal,tactual):
            raise ValueError(
                "actual argument type {} is not compatible with formal argument type {}"
                .format(tactual[0],tformal[0]))

    return ret_type

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

    return ('VOID_TYPE',)

#########################################################################
def fundecl_stmt(node):

    (FUNDECL, (ID, name), type, arglist, body) = node

    symtab.declare(name, type)

    # unpack function type
    (FUNCTION_TYPE, ret_type, arglist_types) = type

    # typecheck body of function
    symtab.push_scope(ret_type=ret_type)
    declare_formal_args(arglist)
    walk(body)
    symtab.pop_scope()

    return None

#########################################################################
def vardecl_stmt(node):

    (VARDECL, (ID, name), type, init_val) = node

    ti = walk(init_val)
    if not safe_assign(type, ti):
        raise ValueError(
            "type {} of initializer is not compatible with declaration type {}"
            .format(ti[0],type[0]))
    symtab.declare(name, type)
    return None

#########################################################################
def arraydecl_stmt(node):

    (ARRAYDECL, (ID, name), type, (LIST, init_val_list)) = node
    (ARRAY_TYPE, base_type, (SIZE, size)) = type

    if not size > 0:
        raise ValueError("illegal array size")

    if len(init_val_list) != size:
        raise ValueError("array size {} and length of initializer {} don't agree"
                    .format(size, len(init_val_list)))

    # walk through initializers and make sure they are type safe
    for ix in range(size):
        ti = walk(init_val_list[ix])
        if not safe_assign(base_type, ti):
            raise ValueError(
                "type {} of initializer is not compatible with declaration type {}"
                .format(ti[0],base_type[0]))

    symtab.declare(name, type)

    return None

#########################################################################
def assign_stmt(node):

    (ASSIGN, storable, exp) = node

    ts = walk(storable)
    te = walk(exp)

    if not safe_assign(ts, te):
        raise ValueError("left type {} is not compatible with right type {}"
                        .format(ts[0],te[0]))

    return None

#########################################################################
def get_stmt(node):

    (GET, storable) = node
    type = walk(storable)

    if type == 'ARRAY_TYPE':
        raise ValueError("arrays not supported in get")

    return None

#########################################################################
def put_stmt(node):

    (PUT, exp) = node

    walk(exp)

    return None

#########################################################################
def call_stmt(node):

    (CALLSTMT, (ID, name), actual_args) = node
    type = symtab.lookup_sym(name)

    if type[0] != 'FUNCTION_TYPE':
        raise ValueError("{} is not a function".format(name))

    check_call(type, actual_args)

    return None

#########################################################################
def return_stmt(node):

    (RETURN, exp) = node

    t = walk(exp)
    ret_type = symtab.lookup_ret_type()
    if t[0] == 'VOID_TYPE' and ret_type[0] == 'VOID_TYPE':
        return None
    elif not safe_assign(ret_type, t):
        raise ValueError(
            "function return type {} is not compatible with return statement type {}"
            .format(ret_type[0], t[0]))
    else:
        return None

#########################################################################
def while_stmt(node):

    (WHILE, cond, body) = node
    assert_match(WHILE, 'WHILE')

    ctype = walk(cond)
    if ctype[0] != 'INTEGER_TYPE':
        raise ValueError("while condition has to be of type INTEGER_TYPE not {}"
                    .format(ctype[0]))
    walk(body)

    return None

#########################################################################
def if_stmt(node):

    (IF, cond, then_stmt, else_stmt) = node

    ctype = walk(cond)
    if ctype[0] != 'INTEGER_TYPE':
        raise ValueError("if condition has to be of type INTEGER_TYPE not {}"
                    .format(ctype[0]))
    walk(then_stmt)
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

    t1 = walk(c1)
    t2 = walk(c2)

    return promote(t1,t2)

#########################################################################
def minus_exp(node):

    (MINUS,c1,c2) = node

    t1 = walk(c1)
    t2 = walk(c2)
    tr = promote(t1,t2)
    if tr[0] not in ['INTEGER_TYPE','FLOAT_TYPE']:
        raise ValueError("operation on type {} not supported"
                        .format(tr[0]))
    return tr

#########################################################################
def mul_exp(node):

    (MUL,c1,c2) = node

    t1 = walk(c1)
    t2 = walk(c2)
    tr = promote(t1,t2)
    if tr[0] not in ['INTEGER_TYPE','FLOAT_TYPE']:
        raise ValueError("operation on type {} not supported"
                        .format(tr[0]))
    return tr

#########################################################################
def div_exp(node):

    (DIV,c1,c2) = node

    t1 = walk(c1)
    t2 = walk(c2)
    tr = promote(t1,t2)
    if tr[0] not in ['INTEGER_TYPE','FLOAT_TYPE']:
        raise ValueError("operation on type {} not supported"
                        .format(tr[0]))
    return tr

#########################################################################
def eq_exp(node):

    (EQ,c1,c2) = node

    walk(c1)
    walk(c2)

    return ('INTEGER_TYPE',)

#########################################################################
def le_exp(node):

    (LE,c1,c2) = node

    walk(c1)
    walk(c2)

    return ('INTEGER_TYPE',)

#########################################################################
def const_exp(node):

    (CONST, type, value) = node

    return type

#########################################################################
def id_exp(node):

    (ID, name) = node

    val = symtab.lookup_sym(name)

    return val

#########################################################################
def call_exp(node):

    (CALLEXP, (ID, name), actual_args) = node

    type = symtab.lookup_sym(name)

    if type[0] != 'FUNCTION_TYPE':
        raise ValueError("{} is not a function".format(name))

    return check_call(type, actual_args)

#########################################################################
def uminus_exp(node):

    (UMINUS, exp) = node

    tr = walk(exp)
    if tr[0] not in ['INTEGER_TYPE','FLOAT_TYPE']:
        raise ValueError("operation on type {} not supported"
                        .format(tr[0]))
    return tr

#########################################################################
def not_exp(node):

    (NOT, exp) = node

    tr = walk(exp)
    if tr[0] not in ['INTEGER_TYPE']:
        raise ValueError("operation on type {} not supported"
                        .format(tr[0]))
    return tr

#########################################################################
def paren_exp(node):

    (PAREN, exp) = node

    # return the value of the parenthesized expression
    return walk(exp)

#########################################################################
def array_access_exp(node):

    (ARRAY_ACCESS, array_exp, (IX, ix)) = node

    type = walk(array_exp)
    ix_type = walk(ix)

    if type[0] != 'ARRAY_TYPE':
        raise ValueError("{} not an array".format(name))

    if ix_type[0] != 'INTEGER_TYPE':
        raise ValueError("array index has to be of type INTEGER_TYPE")

    (ARRAY_TYPE, base_type, size) = type

    return base_type

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
    'STMTLIST'     : stmtlist,
    'NIL'          : nil,
    'FUNDECL'      : fundecl_stmt,
    'VARDECL'      : vardecl_stmt,
    'ARRAYDECL'    : arraydecl_stmt,
    'ASSIGN'       : assign_stmt,
    'GET'          : get_stmt,
    'PUT'          : put_stmt,
    'CALLSTMT'     : call_stmt,
    'RETURN'       : return_stmt,
    'WHILE'        : while_stmt,
    'IF'           : if_stmt,
    'BLOCK'        : block_stmt,
    'CONST'        : const_exp,
    'ID'           : id_exp,
    'CALLEXP'      : call_exp,
    'PAREN'        : paren_exp,
    'PLUS'         : plus_exp,
    'MINUS'        : minus_exp,
    'MUL'          : mul_exp,
    'DIV'          : div_exp,
    'EQ'           : eq_exp,
    'LE'           : le_exp,
    'UMINUS'       : uminus_exp,
    'NOT'          : not_exp,
    'ARRAY_ACCESS' : array_access_exp,
}
