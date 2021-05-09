'''
fold: this is simple constant folder for our Cuppa1 compiler

it is a tree rewriter so at every node function we have to construct
a new node because we are not allowed to update tuples in Python
and we are not sure if the tree below us has changed.
'''

from assertmatch import assert_match

# node functions
#########################################################################
def stmtlst(node):

    (STMTLIST, lst) = node
    assert_match(STMTLIST, 'STMTLIST')

    newlst = []
    for stmt in lst:
        newlst.append(walk(stmt))
    return ('STMTLIST', newlst)

#########################################################################
def nil(node):

    (NIL,) = node
    assert_match(NIL, 'NIL')

    return node # nil nodes are immutable

#########################################################################
def assign_stmt(node):

    (ASSIGN, name_tree, exp) = node
    assert_match(ASSIGN, 'ASSIGN')

    newexp = walk(exp)

    return ('ASSIGN', name_tree, newexp)

#########################################################################
def get_stmt(node):

    (GET, name_tree) = node
    assert_match(GET, 'GET')

    return node # nothing to be rewritten in get nodes

#########################################################################
def put_stmt(node):

    (PUT, exp) = node
    assert_match(PUT, 'PUT')

    newexp = walk(exp)

    return ('PUT', newexp)

#########################################################################
def while_stmt(node):

    (WHILE, cond, body) = node
    assert_match(WHILE, 'WHILE')

    newcond = walk(cond)
    newbody = walk(body)

    return ('WHILE', newcond, newbody)

#########################################################################
def if_stmt(node):

        (IF, cond, s1, s2) = node
        assert_match(IF, 'IF')

        newcond = walk(cond)
        news1 = walk(s1)
        news2 = walk(s2)

        return ('IF', newcond, news1, news2)

#########################################################################
def block_stmt(node):

    (BLOCK, stmtlst) = node
    assert_match(BLOCK, 'BLOCK')

    newstmtlst = walk(stmtlst)

    return ('BLOCK', newstmtlst)

#########################################################################
# Expressions -- try to fold constants
#########################################################################
def plus_exp(node):

    (PLUS, c1, c2) = node
    assert_match(PLUS, 'PLUS')

    newc1 = walk(c1)
    newc2 = walk(c2)

    # if the children are constants -- fold!
    if newc1[0] == 'INTEGER' and newc2[0] == 'INTEGER':
        return ('INTEGER', newc1[1] + newc2[1])
    else:
        return ('PLUS', newc1, newc2)

#########################################################################
def minus_exp(node):

    (MINUS, c1, c2) = node
    assert_match(MINUS, 'MINUS')

    newc1 = walk(c1)
    newc2 = walk(c2)

    # if the children are constants -- fold!
    if newc1[0] == 'INTEGER' and newc2[0] == 'INTEGER':
        return ('INTEGER', newc1[1] - newc2[1])
    else:
        return ('MINUS', newc1, newc2)

#########################################################################
def mult_exp(node):

    (MUL, c1, c2) = node
    assert_match(MUL, 'MUL')

    newc1 = walk(c1)
    newc2 = walk(c2)

    # if the children are constants -- fold!
    if newc1[0] == 'INTEGER' and newc2[0] == 'INTEGER':
        return ('INTEGER', newc1[1] * newc2[1])
    else:
        return ('MUL', newc1, newc2)

#########################################################################
def div_exp(node):

    (DIV, c1, c2) = node
    assert_match(DIV, 'DIV')

    newc1 = walk(c1)
    newc2 = walk(c2)

    # if the children are constants -- fold!
    if newc1[0] == 'INTEGER' and newc2[0] == 'INTEGER':
        return ('INTEGER', newc1[1] // newc2[1]) # integer division
    else:
        return ('DIV', newc1, newc2)

#########################################################################
def eq_exp(node):

    (EQ, c1, c2) = node
    assert_match(EQ, 'EQ')

    newc1 = walk(c1)
    newc2 = walk(c2)

    # if the children are constants -- fold!
    if newc1[0] == 'INTEGER' and newc2[0] == 'INTEGER':
        return ('INTEGER', 1 if newc1[1] == newc2[1] else 0)
    else:
        return ('EQ', newc1, newc2)

#########################################################################
def le_exp(node):

    (LE, c1, c2) = node
    assert_match(LE, 'LE')

    newc1 = walk(c1)
    newc2 = walk(c2)

    # if the children are constants -- fold!
    if newc1[0] == 'INTEGER' and newc2[0] == 'INTEGER':
        return ('INTEGER', 1 if newc1[1] <= newc2[1] else 0)
    else:
        return ('LE', newc1, newc2)

#########################################################################
def integer_exp(node):

    (INTEGER, value) = node
    assert_match(INTEGER, 'INTEGER')

    return node # integer nodes are immutable

#########################################################################
def id_exp(node):

    (ID, name) = node
    assert_match(ID, 'ID')

    return node # id nodes are immutable

#########################################################################
def uminus_exp(node):

    (UMINUS, e) = node
    assert_match(UMINUS, 'UMINUS')

    newe = walk(e)

    return ('UMINUS', newe)

#########################################################################
def not_exp(node):

    (NOT, e) = node
    assert_match(NOT, 'NOT')

    newe = walk(e)

    return ('NOT', newe)

#########################################################################
def paren_exp(node):

    (PAREN, exp) = node
    assert_match(PAREN, 'PAREN')

    newexp = walk(exp)

    return ('PAREN', newexp)

#########################################################################
# walk
#########################################################################
def walk(node):
    node_type = node[0]
    if node_type in dispatch:
        node_function = dispatch[node_type]
        return node_function(node)
    else:
        raise ValueError("walk: unknown tree node type: " + node_type)

# a dictionary to associate tree nodes with node functions
dispatch = {
    'STMTLIST'  : stmtlst,
    'NIL'       : nil,
    'ASSIGN'    : assign_stmt,
    'GET'       : get_stmt,
    'PUT'       : put_stmt,
    'WHILE'     : while_stmt,
    'IF'        : if_stmt,
    'BLOCK'     : block_stmt,
    'INTEGER'   : integer_exp,
    'ID'        : id_exp,
    'UMINUS'    : uminus_exp,
    'NOT'       : not_exp,
    'PAREN'     : paren_exp,
    'PLUS'      : plus_exp,
    'MINUS'     : minus_exp,
    'MUL'       : mult_exp,
    'DIV'       : div_exp,
    'EQ'        : eq_exp,
    'LE'        : le_exp,
}
