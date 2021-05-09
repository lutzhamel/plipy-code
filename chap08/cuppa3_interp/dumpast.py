##################################################################
# this function will print any AST that follows the
#
#      (TYPE [, child1, child2,...])
#
# tuple format for tree nodes.

def dumpast(node):
    _dumpast(node)
    print('')

def _dumpast(node, level=0):

    if isinstance(node, tuple):
        indent(level)
        nchildren = len(node) - 1

        print("(%s" % node[0], end='')

        if nchildren > 0:
            print(" ", end='')

        for c in range(nchildren):
            _dumpast(node[c+1], level+1)
            if c != nchildren-1:
                print(' ', end='')

        print(")", end='')
    elif isinstance(node, list):
        indent(level)
        nchildren = len(node)

        print("[", end='')

        if nchildren > 0:
            print(" ", end='')

        for c in range(nchildren):
            _dumpast(node[c], level+1)
            if c != nchildren-1:
                print(' ', end='')
        print("]", end='')
    else:
        print("%s" % str(node), end='')

def indent(level):
    print('')
    for i in range(level):
        print('  |',end='')
