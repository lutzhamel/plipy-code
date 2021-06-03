from cuppa1_state import state

# pp2: this is the second pass of the Cuppa1 pretty printer that
# generates the output together with the warning

indent_level = 0

#########################################################################
# node functions
#########################################################################
def stmtlist(node):

    (STMTLIST, lst) = node

    code = ''
    for stmt in lst:
        code += walk(stmt)
    return code

#########################################################################
def nil(node):
    (NIL,) = node
    return ''

#########################################################################
def assign_stmt(node):

    (ASSIGN, (ID, name), exp) = node

    exp_code = walk(exp)
    code = indent() + name + ' = ' + exp_code
    if state.symbol_table[name] == 'Defined':
        code += ' // *** '+ name + ' is not used ***'
    code += '\n'
    return code

#########################################################################
def get_stmt(node):

    (GET, (ID, name)) = node

    code = indent() + 'get ' + name
    if state.symbol_table[name] == 'Defined':
        code += ' // *** '+ name + ' is not used ***'
    code += '\n'

    return code

#########################################################################
def put_stmt(node):

    (PUT, exp) = node

    exp_code = walk(exp)
    code = indent() + 'put ' + exp_code + '\n'
    return code

#########################################################################
def while_stmt(node):
    global indent_level

    (WHILE, cond, body) = node

    cond_code = walk(cond)

    indent_level += 1
    body_code = walk(body)
    indent_level -= 1

    code = indent() + 'while (' + cond_code + ')\n' + body_code

    return code

#########################################################################
def if_stmt(node):
    global indent_level

    (IF, cond, s1, s2) = node

    cond_code = walk(cond)

    indent_level += 1
    stmt1_code = walk(s1)
    stmt2_code = walk(s2)
    indent_level -= 1

    code = indent() + 'if (' + cond_code + ')\n' + stmt1_code
    if stmt2_code: # else stmt not nil
        code += indent() + 'else\n' + stmt2_code
    return code

#########################################################################
def block_stmt(node):
    global indent_level
    adjust_level = False

    (BLOCK, s) = node

    if indent_level > 0:
        indent_level -= 1
        adjust_level = True

    indent_level += 1
    code = walk(s)
    indent_level -= 1

    code = indent() + '{\n' + code + indent() + '}\n'

    if adjust_level:
        indent_level += 1

    return code

#########################################################################
def binop_exp(node):

    (OP, c1, c2) = node

    lcode = walk(c1)
    rcode = walk(c2)

    if OP == 'PLUS':
        code = lcode + ' + ' + rcode
    elif OP == 'MINUS':
        code = lcode + ' - ' + rcode
    elif OP == 'MUL':
        code = lcode + ' * ' + rcode
    elif OP == 'DIV':
        code = lcode + ' / ' + rcode
    elif OP == 'EQ':
        code = lcode + ' == ' + rcode
    elif OP == 'LE':
        code = lcode + ' =< ' + rcode
    else:
        raise ValueError("unknown OP")

    return code

#########################################################################
def integer_exp(node):

    (INTEGER, value) = node

    return str(value)

#########################################################################
def id_exp(node):

    (ID, name) = node

    return name

#########################################################################
def uminus_exp(node):

    (UMINUS, e) = node

    code = walk(e)

    return '-' + code

#########################################################################
def not_exp(node):

    (NOT, e) = node

    code = walk(e)

    return 'not ' + code

#########################################################################
def paren_exp(node):

    (PAREN, exp) = node

    exp_code = walk(exp)

    return '(' + exp_code + ')'

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
    'STMTLIST' : stmtlist,
    'NIL'      : nil,
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
def indent():
    s = ''
    for i in range(indent_level):
        s += '   '
    return s

#########################################################################
def init_indent_level():
    global indent_level
    indent_level = 0
