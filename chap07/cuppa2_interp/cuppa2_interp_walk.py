# A tree walker to interpret Cuppa2 programs

from cuppa2_symtab import symbol_table

#########################################################################
# node functions
#########################################################################
def stmtlist(node):

    (STMTLIST, lst) = node

    for stmt in lst:
        walk(stmt)

    return None

#########################################################################
def declare_stmt(node):

    (DECLARE, (ID, name), exp) = node

    value = walk(exp)
    symbol_table.declare_sym(name, value)

    return None

#########################################################################
def assign_stmt(node):

    (ASSIGN, (ID, name), exp) = node

    value = walk(exp)
    symbol_table.update_sym(name, value)

    return None

#########################################################################
def get_stmt(node):

    (GET, (ID, name)) = node

    s = input("Value for " + name + '? ')

    try:
        value = int(s)
    except ValueError:
        raise ValueError("expected an integer value for " + name)

    symbol_table.update_sym(name, value)

    return None

#########################################################################
def put_stmt(node):

    (PUT, exp) = node

    value = walk(exp)
    print("{}".format(value))

    return None

#########################################################################
def while_stmt(node):

    (WHILE, cond, body) = node

    while walk(cond) != 0:
        walk(body)

    return None

#########################################################################
def if_stmt(node):

    (IF, cond, then_stmt, else_stmt) = node

    if walk(cond) != 0:
        walk(then_stmt)
    else:
        walk(else_stmt)
    return None

#########################################################################
def block_stmt(node):

    (BLOCK, stmt_list) = node

    symbol_table.push_scope()
    walk(stmt_list)
    symbol_table.pop_scope()

    return None

#########################################################################
def plus_exp(node):

    (PLUS,c1,c2) = node

    v1 = walk(c1)
    v2 = walk(c2)

    return v1 + v2

#########################################################################
def minus_exp(node):

    (MINUS,c1,c2) = node

    v1 = walk(c1)
    v2 = walk(c2)

    return v1 - v2

#########################################################################
def mul_exp(node):

    (MUL,c1,c2) = node

    v1 = walk(c1)
    v2 = walk(c2)

    return v1 * v2

#########################################################################
def div_exp(node):

    (DIV,c1,c2) = node

    v1 = walk(c1)
    v2 = walk(c2)

    return v1 // v2 # integer division

#########################################################################
def eq_exp(node):

    (EQ,c1,c2) = node

    v1 = walk(c1)
    v2 = walk(c2)

    return 1 if v1 == v2 else 0

#########################################################################
def le_exp(node):

    (LE,c1,c2) = node

    v1 = walk(c1)
    v2 = walk(c2)

    return 1 if v1 <= v2 else 0

#########################################################################
def integer_exp(node):

    (INTEGER, value) = node

    return value

#########################################################################
def id_exp(node):

    (ID, name) = node

    return symbol_table.lookup_sym(name)

#########################################################################
def uminus_exp(node):

    (UMINUS, exp) = node

    val = walk(exp)
    return - val

#########################################################################
def not_exp(node):

    (NOT, exp) = node

    val = walk(exp)
    return 0 if val != 0 else 1

#########################################################################
def paren_exp(node):

    (PAREN, exp) = node

    # return the value of the parenthesized expression
    return walk(exp)

#########################################################################
def nil(node):

    (NIL,) = node

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
