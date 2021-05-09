'''
This module implements the Cuppa5 type coercion system through a set
of tables.  These tables implement the type hierarchy

         INTEGER_TYPE < FLOAT_TYPE < STRING_TYPE
         ARRAY_TYPE
         VOID_TYPE
'''
# types that are supported in arithmetic/local operations
supported_types = [
    'STRING_TYPE',
    'FLOAT_TYPE',
    'INTEGER_TYPE',
    ]

def supported(t):
    if t[0] not in supported_types:
        raise ValueError("operation does not support type {}".format(t[0]))
    else:
        return True

def error(_):
    raise ValueError("internal: type coercion error")

def id(x):
    return x;

# compute the lowest common type for operands of a binary operation
_promote_table = {
  'STRING_TYPE' : {'STRING_TYPE': 'STRING_TYPE', 'FLOAT_TYPE': 'STRING_TYPE', 'INTEGER_TYPE': 'STRING_TYPE'},
  'FLOAT_TYPE'  : {'STRING_TYPE': 'STRING_TYPE', 'FLOAT_TYPE': 'FLOAT_TYPE',  'INTEGER_TYPE': 'FLOAT_TYPE'},
  'INTEGER_TYPE': {'STRING_TYPE': 'STRING_TYPE', 'FLOAT_TYPE': 'FLOAT_TYPE',  'INTEGER_TYPE': 'INTEGER_TYPE'},
 }

# compute the type coercion function given the target and source types
_coercion_table = {
  'STRING_TYPE' : {'STRING_TYPE': id,    'FLOAT_TYPE': str,   'INTEGER_TYPE': str},
  'FLOAT_TYPE'  : {'STRING_TYPE': error, 'FLOAT_TYPE': id,    'INTEGER_TYPE': float},
  'INTEGER_TYPE': {'STRING_TYPE': error, 'FLOAT_TYPE': error, 'INTEGER_TYPE': id},
  }

# compute whether an assignment is safe based on the target and source type
_safe_assign_table = {
  'STRING_TYPE' : {'STRING_TYPE': True,  'FLOAT_TYPE': True,  'INTEGER_TYPE': True},
  'FLOAT_TYPE'  : {'STRING_TYPE': False, 'FLOAT_TYPE': True,  'INTEGER_TYPE': True},
  'INTEGER_TYPE': {'STRING_TYPE': False, 'FLOAT_TYPE': False, 'INTEGER_TYPE': True},
}

def promote(type1, type2):
    supported(type1)
    supported(type2)
    type = (_promote_table.get(type1[0]).get(type2[0]),)
    if type[0] == 'VOID_TYPE':
        raise ValueError("type {} and type {} are not compatible"
                    .format(type1[0],type2[0]))
    return type

def coerce(target, source):
    supported(target)
    supported(source)
    return _coercion_table.get(target[0]).get(source[0])

def safe_assign(target, source):
    # array types are structured types. there is no nice way to do lookups
    # in a table so we have to compute if it safe to assign.
    if target[0] == 'ARRAY_TYPE' and source[0] == 'ARRAY_TYPE':
        (ARRAY_TYPE, ttype, (SIZE, tsize)) = target
        (ARRAY_TYPE, stype, (SIZE, ssize)) = source
        # compare base types and size -- have to be exacty the same!
        if ttype == stype and tsize == ssize:
            return True
        else:
            return False
    else:
        # check for regular operations
        supported(target)
        supported(source)
        return _safe_assign_table.get(target[0]).get(source[0])
