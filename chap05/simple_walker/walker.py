
#########################################################################
def const(node):
    # pattern match the constant node
    (INTEGER, val) = node

    # return the value as an integer value
    return int(val)

#########################################################################
def add(node):
    # pattern match the tree node
    (PLUS, left, right) = node

    # recursively call the walker on the children
    left_val = walk(left)
    right_val = walk(right)

    # return the sum of the values of the children
    return left_val + right_val

#########################################################################
def multiply(node):
    # pattern match the tree node
    (MUL, left, right) = node

    # recursively call the walker on the children
    left_val = walk(left)
    right_val = walk(right)

    # return the product of the values of the children
    return left_val * right_val

#########################################################################
def walk(node):
    # first component of any tree node is its type
    t = node[0]

    # lookup the function for this node
    node_function = dispatch_dictionary[t]

    # now call this function on our node and capture the return value
    val = node_function(node)

    return val

#########################################################################
dispatch_dictionary = {
    'PLUS'    : add,
    'MUL'     : multiply,
    'INTEGER' : const
}
