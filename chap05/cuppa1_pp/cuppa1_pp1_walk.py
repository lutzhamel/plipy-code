from cuppa1_state import state

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

    for stmt in lst:
        walk(stmt)

    return None

#########################################################################
def assign_stmt(node):

    (ASSIGN, (ID, name), exp) = node

    state.symbol_table[name] = 'Defined'
    walk(exp)

    return None

#########################################################################
def get_stmt(node):

    (GET, (ID, name)) = node

    state.symbol_table[name] = 'Defined'

    return None

#########################################################################
def put_stmt(node):

    (PUT, exp) = node

    walk(exp)

    return None

#########################################################################
def while_stmt(node):

    (WHILE, cond, body) = node

    walk(cond)
    walk(body)

    return None

#########################################################################
def if_stmt(node):

    (IF, cond, s1, s2) = node

    walk(cond)
    walk(s1)
    walk(s2)

    return None

#########################################################################
def block_stmt(node):

    (BLOCK, stmt_list) = node

    walk(stmt_list)

    return None

#########################################################################
def binop_exp(node):

    (OP, c1, c2) = node

    walk(c1)
    walk(c2)

    return None

#########################################################################
def id_exp(node):

    (ID, name) = node

    # we found a use scenario of a variable
    state.symbol_table[name] = 'Used'

    return None

#########################################################################
def uminus_exp(node):

    (UMINUS, e) = node

    walk(e)

    return None

#########################################################################
def not_exp(node):

    (NOT, e) = node

    walk(e)

    return None

#########################################################################
def paren_exp(node):

    (PAREN, exp) = node

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
