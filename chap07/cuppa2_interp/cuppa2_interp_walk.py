# A tree walker to interpret Cuppa2 programs

from assertmatch import assert_match
from cuppa2_state import state

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
def declare_stmt(node):

    (DECLARE, (ID, name), exp) = node
    assert_match(DECLARE, 'DECLARE')
    assert_match(ID, 'ID')

    value = walk(exp)
    state.symbol_table.declare_sym(name, value)

    return None

#########################################################################
def assign_stmt(node):

    (ASSIGN, (ID, name), exp) = node
    assert_match(ASSIGN, 'ASSIGN')
    assert_match(ID, 'ID')

    value = walk(exp)
    state.symbol_table.update_sym(name, value)

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

    state.symbol_table.update_sym(name, value)

    return None

#########################################################################
def put_stmt(node):

    (PUT, exp) = node
    assert_match(PUT, 'PUT')

    value = walk(exp)
    print("{}".format(value))

    return None

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

    state.symbol_table.push_scope()
    walk(stmt_list)
    state.symbol_table.pop_scope()

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

    return v1 // v2 # integer division

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

    return state.symbol_table.lookup_sym(name)

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
    assert_match(PAREN, 'PAREN')

    # return the value of the parenthesized expression
    return walk(exp)

#########################################################################
def nil(node):

    (NIL,) = node
    assert_match(NIL, 'NIL')

    # do nothing!

    return None

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
    'STMTLIST' : stmtlist,
    'DECLARE'  : declare_stmt,
    'ASSIGN'   : assign_stmt,
    'GET'      : get_stmt,
    'PUT'      : put_stmt,
    'WHILE'    : while_stmt,
    'IF'       : if_stmt,
    'NIL'      : nil,
    'BLOCK'    : block_stmt,
    'INTEGER'  : integer_exp,
    'ID'       : id_exp,
    'PAREN'    : paren_exp,
    'PLUS'     : plus_exp,
    'MINUS'    : minus_exp,
    'MUL'      : mul_exp,
    'DIV'      : div_exp,
    'EQ'       : eq_exp,
    'LE'       : le_exp,
    'UMINUS'   : uminus_exp,
    'NOT'      : not_exp
}
