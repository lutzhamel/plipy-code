'''
codegen: this is the code generator for our Cuppa1 compiler

The generated code is a list of Exp1bytecode tuples, that means
the codegen walker generates lists of tuples for statements but
strings for expressions.
'''

from cuppa2_symtab import symbol_table

# node functions
#########################################################################
def stmtlst(node):

    (STMTLIST, lst) = node

    outlst = []
    for stmt in lst:
        outlst += walk(stmt)
    return outlst

#########################################################################
def nil(node):

    (NIL,) = node

    return []

#########################################################################
def declare_stmt(node):

    (DECLARE, (ID, name), init_val) = node

    symbol_table.declare_sym(name)
    scoped_name = symbol_table.lookup_sym(name)
    value = walk(init_val)
    code = [('store', scoped_name, str(value))]

    return code

#########################################################################
def assign_stmt(node):

    (ASSIGN, (ID, name), exp) = node

    exp_code = walk(exp)
    scoped_name = symbol_table.lookup_sym(name)
    code = [('store', scoped_name, exp_code)]

    return code

#########################################################################
def get_stmt(node):

    (GET, (ID, name)) = node

    scoped_name = symbol_table.lookup_sym(name)
    code = [('input', scoped_name)]

    return code

#########################################################################
def put_stmt(node):

    (PUT, exp) = node

    exp_code = walk(exp)

    code = [('print', exp_code)]

    return code

#########################################################################
def while_stmt(node):

    (WHILE, cond, body) = node

    top_label = label()
    bottom_label = label()
    cond_code = walk(cond)
    body_code = walk(body)
    code = []

    code += [(top_label + ':',)]
    code += [('jumpf', cond_code, bottom_label)]
    code += body_code
    code += [('jump', top_label)]
    code += [(bottom_label + ':',)]
    code += [('noop',)]

    return code

#########################################################################
def if_stmt(node):

    (IF, cond, then_stmt, else_stmt) = node

    else_label = label()
    end_label = label()
    cond_code = walk(cond)
    then_code = walk(then_stmt)
    else_code = walk(else_stmt)
    code = []

    # Note: in the following code we take advantage of the
    # fact that in Python: bool([]) == False
    # that is an empty instruction list for else_code is
    # interpreted as False.

    code += [('jumpf', cond_code, else_label if else_code else end_label)]
    code += then_code
    if else_code:
        code += [('jump', end_label)]
        code += [(else_label + ':',)]
        code += else_code
    code += [(end_label + ':',)]
    code += [('noop',)]

    return code

#########################################################################
def block_stmt(node):

    (BLOCK, s) = node

    symbol_table.push_scope()
    code = walk(s)
    symbol_table.pop_scope()

    return code

#########################################################################
def binop_exp(node):

    (OP, c1, c2) = node
    if OP not in ['PLUS', 'MINUS', 'MUL', 'DIV', 'EQ', 'LE']:
        raise ValueError('pattern match failed on ' + OP)

    lcode = walk(c1)
    rcode = walk(c2)

    if OP == 'PLUS':
        OPSYM = '+'
    elif OP == 'MINUS':
        OPSYM = '-'
    elif OP == 'MUL':
        OPSYM = '*'
    elif OP == 'DIV':
        OPSYM = '/'
    elif OP == 'EQ':
        OPSYM = '=='
    elif OP == 'LE':
        OPSYM = '=<'

    code = OPSYM + ' ' + lcode + ' ' + rcode
    return code

#########################################################################
def integer_exp(node):

    (INTEGER, value) = node

    # parens necessary due to unary minus
    if value < 0:
        return '(' + str(value) + ')'
    else:
        return str(value)

#########################################################################
def id_exp(node):

    (ID, name) = node

    scoped_name = symbol_table.lookup_sym(name)

    return scoped_name

#########################################################################
def uminus_exp(node):

    (UMINUS, e) = node

    code = walk(e)
    return '(-' + code + ')'

#########################################################################
def not_exp(node):

    (NOT, e) = node

    code = walk(e)

    return '!' + code

#########################################################################
def paren_exp(node):

    (PAREN, exp) = node

    exp_code = walk(exp)

    return exp_code

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
    'NIL'      : nil,
    'DECLARE'  : declare_stmt,
    'ASSIGN'   : assign_stmt,
    'GET'      : get_stmt,
    'PUT'      : put_stmt,
    'WHILE'    : while_stmt,
    'IF'       : if_stmt,
    'BLOCK'    : block_stmt,
    'INTEGER'  : integer_exp,
    'ID'       : id_exp,
    'UMINUS'   : uminus_exp,
    'NOT'      : not_exp,
    'PAREN'    : paren_exp,
    'PLUS'     : binop_exp,
    'MINUS'    : binop_exp,
    'MUL'      : binop_exp,
    'DIV'      : binop_exp,
    'EQ'       : binop_exp,
    'LE'       : binop_exp,
}

#########################################################################
label_id = 0

def label():
    global label_id
    s =  'L' + str(label_id)
    label_id += 1
    return s
