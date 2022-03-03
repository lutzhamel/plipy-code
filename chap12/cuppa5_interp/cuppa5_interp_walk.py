# A tree walker to interpret Cuppa5 programs

from cuppa5_symtab import symtab
from cuppa5_types import coerce, promote

#########################################################################
# Use the exception mechanism to return values from function calls

class ReturnValue(Exception):

    def __init__(self, value):
        self.value = value

    def __str__(self):
        return(repr(self.value))

#########################################################################
def location(storable):
    '''
    we are interested in the locations of storable because we
    perhaps want to update them.  we have two categories
    of locations for storables:
        a[i] -- the is a memory access of the array a
        a    -- we are referencing the storable by name (id)
    '''

    if storable[0] == 'ARRAY_ACCESS':
        # memory access
        (ARRAY_ACCESS, name_exp, (IX, ix)) = storable
        (tmemory, memory) = walk(name_exp)
        (t,offset) = walk(ix)
        return ('LOCATION', ('MEMORY', (tmemory,memory)), ('OFFSET', offset))
    else:
        # access via name
        (ID, name) = storable
        return ('LOCATION', ('ID', name), ('NIL',))

#########################################################################
def update_storable(storable, exp):
    '''
    Update a storable location with the value of exp. We have three cases
    to contend with:
       (a) a[i] = v # where a is an array and v is a scalar
       (b) x = v    # where x and v are scalars
       (c) a = b    # where a and b are arrays
    The function 'location' distinguishes between the case (a) and the
    other two cases. Case (a) maps into 'MEMORY' and the other two
    cases map into 'ID'.  Cases (b) and (c) are then distinguished
    when trying to do the actual assignment.
    '''

    # evaluate source
    (t,v) = walk(exp)

    # get information about target
    (LOCATION, location_type, offset) = location(storable)

    if location_type[0] == 'MEMORY':
        # we are copying a value into a single element, e.g.
        #   a[i] = x
        (MEMORY, (tmemory, memory)) = location_type
        (ARRAY_TYPE, base_type, (SIZE, size)) = tmemory

        if offset[1] < 0 or offset[1] > size-1:
            raise ValueError("array index {}[{}] out of bounds"
                        .format(name, offset))
        # update memory location of array
        memory[offset[1]] = v
    elif location_type[0] == 'ID':
        # we are copying value(s) based on name, e.g.
        #     a = x
        (ID, name) = location_type
        val = symtab.lookup_sym(name)
        if val[0] == 'CONST':
            # id refers to a scalar, copy scalar value
            (CONST, ts, (VALUE, value)) = val
            symtab.update_sym(name, ('CONST', ts, ('VALUE', coerce(ts,t)(v))))
        elif val[0] == 'ARRAYVAL':
            # id refers to an array, copy the whole array
            (ARRAYVAL, ts, (LIST, smemory)) = val
            # we are copying the whole array
            # Note: we don't want to lose the reference to our memory
            # so we are copying each element separately
            (ARRAY_TYPE, base_type, (SIZE, size)) = ts
            # Note: we could use Python shallow array copy here but
            # this makes it explicit that we are copying elements.
            # we CANNOT copy Python list reference because then both
            # arrays in Cuppa5 would share the same memory.
            for i in range(size):
                smemory[i] = v[i]
        else:
            raise ValueError("internal error on {}".format(val))
    else:
        raise ValueError("internal error on {}".format(location_type))

#########################################################################
def value_list(ll):
    '''
    convert a list of Cuppa5 structures into a list of Python values
    '''
    output_list = list()
    for e in ll:
        (t,v) = walk(e)
        output_list.append(v)

    return output_list

#########################################################################
def eval_actual_args(args):
    '''
    Walk the list of actual arguments, evaluate them, and
    return a list with the evaluated actual values
    '''
    (LIST, ll) = args
    outlist = []
    for e in ll:
        v = walk(e)
        outlist.append(v)

    return ('LIST', outlist)

#########################################################################
def declare_formal_args(formal_args, actual_val_args):
    '''
    Walk the formal argument list and declare the identifiers on that
    list using the corresponding actual args as initial values.
    NOTE: this is where we implement by-value argument passing for
          non-array arguments and by-reference passing for array arguments
    NOTE: the type coercion on scalars implements subtype polymorphism for functions
    '''
    (LIST, fl) = formal_args
    (LIST, avl) = actual_val_args

    for ((FORMALARG,tf,(ID,fs)), (ta,va)) in zip(fl,avl):
        # arrays are called by-reference, we use the memory
        # of the actual argument to declare the formal argument array
        if tf[0] == 'ARRAY_TYPE':
            symtab.declare(fs, ('ARRAYVAL', tf, ('LIST', va)))
        else:
            symtab.declare(fs, ('CONST', tf, ('VALUE', coerce(tf,ta)(va))))

#########################################################################
def handle_call(name, actual_arglist):
    '''
    handle calls for both call statements and call expressions.
    '''
    # unpack the funval and type tuples
    (FUNVAL, type, formal_arglist, body, context) = symtab.lookup_sym(name)
    (FUNCTION_TYPE, ret_type, arg_types) = type

    # set up the environment for static scoping and then execute the function
    actual_val_args = eval_actual_args(actual_arglist)
    save_symtab = symtab.get_config()
    symtab.set_config(context)
    symtab.push_scope(ret_type)
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
    for stmt in lst:
        walk(stmt)
    return None

#########################################################################
def nil(node):

    (NIL,) = node
    return ('VOID_TYPE', None)

#########################################################################
def fundecl_stmt(node):

    (FUNDECL, (ID, name), type, arglist, body) = node

    context = symtab.get_config()
    funval = ('FUNVAL', type, arglist, body, context)
    symtab.declare(name, funval)

    return None

#########################################################################
def vardecl_stmt(node):

    (VARDECL, (ID, name), type, init_val) = node

    (ti, vi) = walk(init_val)
    symtab.declare(name, ('CONST', type, ('VALUE', coerce(type,ti)(vi))))

    return None

#########################################################################
def arraydecl_stmt(node):

    (ARRAYDECL, (ID, name), array_type, (LIST, init_val_list)) = node

    # we use the memory allocated for the list of initializers
    # as the memory for the array in the symbol table.
    # therefore we bind the list into the symbol table as
    # part of the declaration
    # Note: we only bind actual Python values into the symbol table,
    # therefore we need to convert the init_val_list into a list of values.

    symtab.declare(name,
                    ('ARRAYVAL',
                     array_type,
                     ('LIST', value_list(init_val_list))))

    return None

#########################################################################
def assign_stmt(node):

    (ASSIGN, storable, exp) = node
    update_storable(storable, exp)
    return None

#########################################################################
def get_stmt(node):

    (GET, (ID, name)) = node
    s = input("Value for " + name + '? ')
    try:
        # cannot use coerce here because that would be going
        # down the type hierarchy which is not supported
        if type[0] == 'STRING_TYPE':
            new_value = s
        elif type[0] == 'FLOAT_TYPE':
            new_value = float(s)
        elif type[0] == 'INTEGER_TYPE':
            new_value = int(s)
        else:
            raise ValueError("input not supported for this type")
    except ValueError:
        raise ValueError("expected a {} value for {}"
                .format(type[0], name))
    symtab.update_sym(name, ('CONST', type, ('VALUE', new_value)))
    return None

#########################################################################
def put_stmt(node):

    (PUT, exp) = node
    (type, value) = walk(exp)
    print(value)

    return None

#########################################################################
def call_stmt(node):

    (CALLSTMT, (ID, name), actual_args) = node
    handle_call(name, actual_args)
    return None

#########################################################################
def return_stmt(node):

    (RETURN, exp) = node

    (t,v) = walk(exp)
    ret_type = symtab.lookup_ret_type()

    if ret_type[0] == 'VOID_TYPE':
        raise ReturnValue(None)
    elif ret_type[0] == 'ARRAY_TYPE':
        # array types have to match exactly according to the
        # type checker therefore we can just copy the type-value
        # pair without coercion
        raise ReturnValue((t,v))
    else:
        raise ReturnValue((ret_type, coerce(ret_type,t)(v)))

#########################################################################
def while_stmt(node):

    (WHILE, cond, body) = node

    while walk(cond)[1]:
        walk(body)

    return None

#########################################################################
def if_stmt(node):

    (IF, cond, then_stmt, else_stmt) = node

    if walk(cond)[1]:
        walk(then_stmt)
    else:
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

    (t1,v1) = walk(c1)
    (t2,v2) = walk(c2)

    t = promote(t1,t2)

    return (t, coerce(t,t1)(v1) + coerce(t,t2)(v2))

#########################################################################
def minus_exp(node):

    (MINUS,c1,c2) = node

    (t1,v1) = walk(c1)
    (t2,v2) = walk(c2)

    t = promote(t1,t2)

    return (t, coerce(t,t1)(v1) - coerce(t,t2)(v2))

#########################################################################
def mul_exp(node):

    (MUL,c1,c2) = node

    (t1,v1) = walk(c1)
    (t2,v2) = walk(c2)

    t = promote(t1,t2)

    return (t, coerce(t,t1)(v1) * coerce(t,t2)(v2))

#########################################################################
def div_exp(node):

    (DIV,c1,c2) = node

    (t1,v1) = walk(c1)
    (t2,v2) = walk(c2)

    t = promote(t1,t2)

    if t == 'INTEGER_TYPE':
        return ('INTEGER_TYPE', v1 // v2)
    else:
        return (t, coerce(t,t1)(v1) / coerce(t,t2)(v2))

#########################################################################
def eq_exp(node):

    (EQ,c1,c2) = node

    (t1,v1) = walk(c1)
    (t2,v2) = walk(c2)
    t = promote(t1, t2)

    if coerce(t,t1)(v1) == coerce(t,t2)(v2):
        return ('INTEGER_TYPE', 1)
    else:
        return ('INTEGER_TYPE', 0)

#########################################################################
def le_exp(node):

    (LE,c1,c2) = node

    (t1,v1) = walk(c1)
    (t2,v2) = walk(c2)
    t = promote(t1, t2)

    if coerce(t,t1)(v1) <= coerce(t,t2)(v2):
        return ('INTEGER_TYPE', 1)
    else:
        return ('INTEGER_TYPE', 0)

#########################################################################
def const_exp(node):

    (CONST, type, (VALUE, value)) = node
    return (type, value)

#########################################################################
def id_exp(node):

    (ID, name) = node
    (symtabrec_type, type, (val_type, value)) = symtab.lookup_sym(name)

    return (type, value)

#########################################################################
def call_exp(node):

    (CALLEXP, (ID, name), actual_args) = node

    return_value = handle_call(name, actual_args)

    if not return_value:
        raise ValueError("No return value from function {}".format(name))
    else:
        return return_value

#########################################################################
def uminus_exp(node):

    (UMINUS, exp) = node
    (type, val) = walk(exp)

    return (type, - val)

#########################################################################
def not_exp(node):

    (NOT, exp) = node
    (type, val) = walk(exp)

    return ('INTEGER_TYPE', 0) if val else ('INTEGER_TYPE', 1)

#########################################################################
def paren_exp(node):

    (PAREN, exp) = node
    # return the (type,value) of the parenthesized expression
    return walk(exp)

#########################################################################
def array_access_exp(node):

    (ARRAY_ACCESS, array_exp, (IX, ix)) = node

    (tarray, varray) = walk(array_exp)
    (tix, vix) = walk(ix)

    (ARRAY_TYPE, base_type, (SIZE, size)) = tarray
    if vix < 0 or vix > size-1:
        raise ValueError("array index {} out of bounds".format(vix))

    return (base_type, varray[vix])

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
