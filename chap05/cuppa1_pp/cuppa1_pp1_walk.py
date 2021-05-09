from cuppa1_state import state
from assertmatch import assert_match

# pp1: this is the first pass of the Cuppa1 pretty printer that marks
# variables in one of three states:
#   None - not used, not defined
#   Used - used in an expression
#   Defined - defined before usage

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
def assign_stmt(node):

    (ASSIGN, (ID, name), exp) = node
    assert_match(ASSIGN, 'ASSIGN')
    assert_match(ID, 'ID')

    state.symbol_table[name] = 'Defined'
    walk(exp)

    return None

#########################################################################
def get_stmt(node):

    (GET, (ID, name)) = node
    assert_match(GET, 'GET')
    assert_match(ID, 'ID')

    state.symbol_table[name] = 'Defined'

    return None

#########################################################################
def put_stmt(node):

    (PUT, exp) = node
    assert_match(PUT, 'PUT')

    walk(exp)

    return None

#########################################################################
def while_stmt(node):

    (WHILE, cond, body) = node
    assert_match(WHILE, 'WHILE')

    walk(cond)
    walk(body)

    return None

#########################################################################
def if_stmt(node):

    (IF, cond, s1, s2) = node
    assert_match(IF, 'IF')

    walk(cond)
    walk(s1)
    walk(s2)

    return None

#########################################################################
def block_stmt(node):

    (BLOCK, stmt_list) = node
    assert_match(BLOCK, 'BLOCK')

    walk(stmt_list)

    return None

#########################################################################
def binop_exp(node):

    (OP, c1, c2) = node
    if OP not in ['PLUS', 'MINUS', 'MUL', 'DIV', 'EQ', 'LE']:
        raise ValueError("pattern match failed on " + OP)

    walk(c1)
    walk(c2)

    return None

#########################################################################
def id_exp(node):

    (ID, name) = node
    assert_match(ID, 'ID')

    # we found a use scenario of a variable
    state.symbol_table[name] = 'Used'

    return None

#########################################################################
def uminus_exp(node):

    (UMINUS, e) = node
    assert_match(UMINUS, 'UMINUS')

    walk(e)

    return None

#########################################################################
def not_exp(node):

    (NOT, e) = node
    assert_match(NOT, 'NOT')

    walk(e)

    return None

#########################################################################
def paren_exp(node):

    (PAREN, exp) = node
    assert_match(PAREN, 'PAREN')

    walk(exp)

    return None

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
    'STMTLIST'    : stmtlist,
    'ASSIGN'      : assign_stmt,
    'GET'         : get_stmt,
    'PUT'         : put_stmt,
    'WHILE'       : while_stmt,
    'IF'          : if_stmt,
    'NIL'         : lambda node : None,
    'BLOCK'       : block_stmt,
    'INTEGER'     : lambda node : None,
    'ID'          : id_exp,
    'UMINUS'      : uminus_exp,
    'NOT'         : not_exp,
    'PAREN'       : paren_exp,
    'PLUS'        : binop_exp,
    'MINUS'       : binop_exp,
    'MUL'         : binop_exp,
    'DiV'         : binop_exp,
    'EQ'          : binop_exp,
    'LE'          : binop_exp
}
