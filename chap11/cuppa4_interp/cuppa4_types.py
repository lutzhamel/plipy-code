'''
This module implements the Cuppa4 type coercion system through a set
of tables.  These tables implement the type hierarchy

         integer < float < string
         void
'''
supported_types = [
    'STRING_TYPE',
    'FLOAT_TYPE',
    'INTEGER_TYPE',
    'VOID_TYPE',
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

# compute the common type for operands of a binary operation
_promote_table = {
  'STRING_TYPE' : {'STRING_TYPE': 'STRING_TYPE', 'FLOAT_TYPE': 'STRING_TYPE', 'INTEGER_TYPE': 'STRING_TYPE',  'VOID_TYPE': 'VOID_TYPE'},
  'FLOAT_TYPE'  : {'STRING_TYPE': 'STRING_TYPE', 'FLOAT_TYPE': 'FLOAT_TYPE',  'INTEGER_TYPE': 'FLOAT_TYPE',   'VOID_TYPE': 'VOID_TYPE'},
  'INTEGER_TYPE': {'STRING_TYPE': 'STRING_TYPE', 'FLOAT_TYPE': 'FLOAT_TYPE',  'INTEGER_TYPE': 'INTEGER_TYPE', 'VOID_TYPE': 'VOID_TYPE'},
  'VOID_TYPE'   : {'STRING_TYPE': 'VOID_TYPE',   'FLOAT_TYPE': 'VOID_TYPE',   'INTEGER_TYPE': 'VOID_TYPE',    'VOID_TYPE': 'VOID_TYPE'},
}

# compute the type coercion function given the target and source types
_coercion_table = {
  'STRING_TYPE' : {'STRING_TYPE': id,    'FLOAT_TYPE': str,   'INTEGER_TYPE': str,   'VOID_TYPE': error},
  'FLOAT_TYPE'  : {'STRING_TYPE': error, 'FLOAT_TYPE': id,    'INTEGER_TYPE': float, 'VOID_TYPE': error},
  'INTEGER_TYPE': {'STRING_TYPE': error, 'FLOAT_TYPE': error, 'INTEGER_TYPE': id,    'VOID_TYPE': error},
  'VOID_TYPE'   : {'STRING_TYPE': error, 'FLOAT_TYPE': error, 'INTEGER_TYPE': error, 'VOID_TYPE': error},
}

# compute whether an assignment is safe based on the target and source type
_safe_assign_table = {
  'STRING_TYPE' : {'STRING_TYPE': True,  'FLOAT_TYPE': True,  'INTEGER_TYPE': True,  'VOID_TYPE': False},
  'FLOAT_TYPE'  : {'STRING_TYPE': False, 'FLOAT_TYPE': True,  'INTEGER_TYPE': True,  'VOID_TYPE': False},
  'INTEGER_TYPE': {'STRING_TYPE': False, 'FLOAT_TYPE': False, 'INTEGER_TYPE': True,  'VOID_TYPE': False},
  'VOID_TYPE'   : {'STRING_TYPE': False, 'FLOAT_TYPE': False, 'INTEGER_TYPE': False, 'VOID_TYPE': False},
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
    supported(target)
    supported(source)
    return _safe_assign_table.get(target[0]).get(source[0])
