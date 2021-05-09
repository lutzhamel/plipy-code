#########################################################################
# symbol table for Cuppa5
#
# it is a scoped symbol table with a dictionary at each scope level
#
#########################################################################

CURR_SCOPE = 0

class SymTab:

    def __init__(self):
        self.initialize()

    def initialize(self):
        # global scope dictionary must always be present
        self.scoped_symtab = [({},None)]

    def get_config(self):
        # we make a shallow copy of the symbol table
        return list(self.scoped_symtab)

    def set_config(self, c):
        self.scoped_symtab = c

    def push_scope(self, ret_type=None):
        # push a new dictionary onto the stack - stack grows to the left
        # Note: every block is associated with a return type
        # even if the return type is None.  If no return
        # type is given in the push instruction then we inherit
        # the return type of the outer block.
        if not ret_type:
            ret_type = self.lookup_ret_type()
        self.scoped_symtab.insert(CURR_SCOPE,({},ret_type))

    def pop_scope(self):
        # pop the left most dictionary off the stack
        if len(self.scoped_symtab) == 1:
            raise ValueError("cannot pop the global scope")
        else:
            self.scoped_symtab.pop(CURR_SCOPE)

    def declare(self, sym, init):
        # declare a symbol in the current scope: dict @ position 0

        # first we need to check whether the symbol was already declared
        # at this scope
        if sym in self.scoped_symtab[CURR_SCOPE][0]:
            raise ValueError("symbol {} already declared".format(sym))

        # enter the symbol in the current scope
        self.scoped_symtab[CURR_SCOPE][0][sym] = init

    def lookup_sym(self, sym):
        # find the first occurence of sym in the symtab stack
        # and return the associated value

        n_scopes = len(self.scoped_symtab)

        for scope in range(n_scopes):
            if sym in self.scoped_symtab[scope][0]:
                val = self.scoped_symtab[scope][0].get(sym)
                return val

        # not found
        raise ValueError("{} was not declared".format(sym))

    def update_sym(self, sym, val):
        # find the first occurence of sym in the symtab stack
        # and update the associated value

        n_scopes = len(self.scoped_symtab)

        for scope in range(n_scopes):
            if sym in self.scoped_symtab[scope][0]:
                self.scoped_symtab[scope][0][sym] = val
                return

        # not found
        raise ValueError("{} was not declared".format(sym))

    def lookup_ret_type(self):
        return self.scoped_symtab[CURR_SCOPE][1]

symtab = SymTab()
