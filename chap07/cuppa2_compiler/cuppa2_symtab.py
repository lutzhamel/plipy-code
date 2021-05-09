#########################################################################
# symbol table for Cuppa2
#
# it is a scoped symbol table with a dictionary at each scope level
#
#########################################################################

CURR_SCOPE = 0

def create_prefix(n):
    prefix = 'R$'
    for i in range(n):
        prefix += '$'
    return prefix

class SymTab:

    #-------
    def __init__(self):
        # global scope dictionary must always be present
        self.scoped_symtab = [{}]

    #-------
    def push_scope(self):
        # push a new dictionary onto the stack - stack grows to the left
        self.scoped_symtab.insert(CURR_SCOPE,{})

    #-------
    def pop_scope(self):
        # pop the left most dictionary off the stack
        if len(self.scoped_symtab) == 1:
            raise ValueError("cannot pop the global scope")
        else:
            self.scoped_symtab.pop(CURR_SCOPE)

    #-------
    def declare_sym(self, sym):
        # declare the symbol in the current scope: dict @ position 0
        
        # first we need to check whether the symbol was already declared
        # at this scope
        if sym in self.scoped_symtab[CURR_SCOPE]:
            raise ValueError("symbol {} already declared".format(sym))
        
        # enter the symbol in the current scope
        n_scopes = len(self.scoped_symtab)
        prefix = create_prefix(n_scopes-1)
        scope_dict = self.scoped_symtab[CURR_SCOPE]
        scope_dict[sym] = prefix + sym # value is the prefixed name

    #-------
    def lookup_sym(self, sym):
        # find the first occurence of sym in the symtab stack
        # and return the associated value

        n_scopes = len(self.scoped_symtab)
    
        # for the compiler version of the symbols we do not
        # return values but a scope prefix
        for scope in range(n_scopes):
            if sym in self.scoped_symtab[scope]:
                val = self.scoped_symtab[scope].get(sym)
                return val

        # not found
        raise ValueError("{} was not declared".format(sym))

#########################################################################


