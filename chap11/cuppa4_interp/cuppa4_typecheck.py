# A tree walker to typecheck Cuppa4 programs

from cuppa4_symtab import symtab
from cuppa4_types import promote, safe_assign
from assertmatch import assert_match


#########################################################################
def declare_formal_args(formal_args):
    (LIST, fl) = formal_args
    assert_match(LIST, 'LIST')

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
                "actual argument type {} is not compatible with \
                formal argument type {}"
                .format(tactual[0],tformal[0]))
                
    return ret_type

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

    return ('VOID_TYPE',)

#########################################################################
def fundecl_stmt(node):

    (FUNDECL, (ID, name), type, arglist, body) = node
    assert_match(FUNDECL, 'FUNDECL')
    assert_match(ID, 'ID')

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
    assert_match(VARDECL, 'VARDECL')
    assert_match(ID, 'ID')

    ti = walk(init_val)
    if not safe_assign(type, ti):
        raise ValueError(
            "type {} of initializer is not compatible with declaration type {}"
            .format(ti[0],type[0]))
    symtab.declare(name, type)
    return None

#########################################################################
def assign_stmt(node):

    (ASSIGN, name_exp, exp) = node
    assert_match(ASSIGN, 'ASSIGN')

    tn = walk(name_exp)
    te = walk(exp)

    if not safe_assign(tn, te):
        raise ValueError("left type {} is not compatible with right type {}"
                        .format(tn[0],te[0]))

    return None

#########################################################################
def get_stmt(node):

    (GET, name_exp) = node
    assert_match(GET, 'GET')

    walk(name_exp)

    return None

#########################################################################
def put_stmt(node):

    (PUT, exp) = node
    assert_match(PUT, 'PUT')

    walk(exp)

    return None

#########################################################################
def call_stmt(node):

    (CALLSTMT, name_exp, actual_args) = node
    assert_match(CALLSTMT, 'CALLSTMT')

    check_call(walk(name_exp), actual_args)

    return None

#########################################################################
def return_stmt(node):

    (RETURN, exp) = node
    assert_match(RETURN, 'RETURN')

    t = walk(exp)
    ret_type = symtab.lookup_ret_type()
    if t[0] == ret_type[0]:
        # this is for the case void <- void
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
    assert_match(IF, 'IF')

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
    assert_match(BLOCK, 'BLOCK')

    symtab.push_scope()
    walk(stmt_list)
    symtab.pop_scope()
    return None

#########################################################################
def plus_exp(node):

    (PLUS,c1,c2) = node
    assert_match(PLUS, 'PLUS')

    t1 = walk(c1)
    t2 = walk(c2)

    return promote(t1,t2)

#########################################################################
def minus_exp(node):

    (MINUS,c1,c2) = node
    assert_match(MINUS, 'MINUS')

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
    assert_match(MUL, 'MUL')

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
    assert_match(DIV, 'DIV')

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
    assert_match(EQ, 'EQ')

    walk(c1)
    walk(c2)

    return ('INTEGER_TYPE',)

#########################################################################
def le_exp(node):

    (LE,c1,c2) = node
    assert_match(LE, 'LE')

    walk(c1)
    walk(c2)

    return ('INTEGER_TYPE',)

#########################################################################
def const_exp(node):

    (CONST, type, value) = node
    assert_match(CONST, 'CONST')

    return type

#########################################################################
def id_exp(node):

    (ID, name) = node
    assert_match(ID, 'ID')

    val = symtab.lookup_sym(name)

    return val

#########################################################################
def call_exp(node):

    (CALLEXP, name_exp, actual_args) = node
    assert_match(CALLEXP, 'CALLEXP')

    tf = walk(name_exp)

    return check_call(tf, actual_args)

#########################################################################
def uminus_exp(node):

    (UMINUS, exp) = node
    assert_match(UMINUS, 'UMINUS')

    tr = walk(exp)
    if tr[0] not in ['INTEGER_TYPE','FLOAT_TYPE']:
        raise ValueError("operation on type {} not supported"
                        .format(tr[0]))
    return tr

#########################################################################
def not_exp(node):

    (NOT, exp) = node
    assert_match(NOT, 'NOT')

    tr = walk(exp)
    if tr[0] not in ['INTEGER_TYPE']:
        raise ValueError("operation on type {} not supported"
                        .format(tr[0]))
    return tr

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
