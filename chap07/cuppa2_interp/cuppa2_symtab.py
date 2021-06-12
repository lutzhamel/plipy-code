#########################################################################
# symbol table for Cuppa2
#
# it is a scoped symbol table with a dictionary at each scope level
#
#########################################################################

CURR_SCOPE = 0

class SymTab:

    #-------
    def __init__(self):
        self.initialize()

    #-------
    def initialize(self):
        # global scope dictionary must always be present
        self.scoped_symtab = [{}]

    #-------
    def push_scope(self):
        # push a new dictionary onto the stack
        self.scoped_symtab.insert(CURR_SCOPE,{})

    #-------
    def pop_scope(self):
        # pop dictionary of current scope off the stack
        if len(self.scoped_symtab) == 1:
            raise ValueError("cannot pop the global scope")
        else:
            self.scoped_symtab.pop(CURR_SCOPE)

    #-------
    def declare_sym(self, sym, init):
        # declare the symbol in the current scope
        
        # first we need to check whether the symbol was already declared
        # at this scope
        if sym in self.scoped_symtab[CURR_SCOPE]:
            raise ValueError("symbol {} already declared".format(sym))

        # enter the symbol in the current scope
        scope_dict = self.scoped_symtab[CURR_SCOPE]
        scope_dict[sym] = init

    #-------
    def lookup_sym(self, sym):
        # find the first occurence of sym in the symtab stack
        # and return the associated value

        n_scopes = len(self.scoped_symtab)

        for scope in range(n_scopes):
            if sym in self.scoped_symtab[scope]:
                val = self.scoped_symtab[scope].get(sym)
                return val

        # not found
        raise ValueError("{} was not declared".format(sym))

    #-------
    def update_sym(self, sym, val):
        # find the first occurence of sym in the symtab stack
        # and update the associated value

        n_scopes = len(self.scoped_symtab)

        for scope in range(n_scopes):
            if sym in self.scoped_symtab[scope]:
                scope_dict = self.scoped_symtab[scope]
                scope_dict[sym] = val
                return

        # not found
        raise ValueError("{} was not declared".format(sym))

#########################################################################
symbol_table = SymTab()
