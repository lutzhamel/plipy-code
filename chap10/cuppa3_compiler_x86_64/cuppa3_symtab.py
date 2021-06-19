#########################################################################
# symbol table for Cuppa3
#
# it is a scoped symbol table with a dictionary at each scope level
#
#########################################################################

CURR_SCOPE = 0

class SymTab:

    def __init__(self):
        # global scope dictionary must always be present
        self.scoped_symtab = [{}]
        # keep track of wether we are in a function declaration of not
        self.in_function = False
        # counter used to generate unique global names
        self.temp_cnt = 0
        # counter to compute the frameoffset of function local variables
        self.offset_cnt = None
        # list of global variables with their sizes to generate the
        # .data segment for GNU as, stored as a tuple (<name>, <size in bytes>)
        self.global_vars = list()

    #####################################################################
    # frame functions

    def make_target_name(self):
        if self.in_function:
            # in functions all function local variables are on the stack
            name = str(self.offset_cnt*8)+"(%rsp)"
            self.offset_cnt += 1
        else:
            # global variable
            name = "t$" + str(self.temp_cnt)
            self.temp_cnt += 1
        return name

    def get_frame_size(self):
        if not self.offset_cnt:
            raise ValueError("frame size only valid within functions")
        return self.offset_cnt

    #####################################################################
    # scope manipulation functions

    def push_scope(self):
        '''
        push a new dictionary onto the stack -- top-of-stack
        is at the beginning of the list.
        '''
        self.scoped_symtab.insert(CURR_SCOPE,{})

    def pop_scope(self):
        '''
        pop the left most dictionary off the stack
        '''
        if len(self.scoped_symtab) == 1:
            raise ValueError("cannot pop the global scope")
        else:
            self.scoped_symtab.pop(CURR_SCOPE)

    def enter_function(self):
        '''
        record that we are in a function def, push a new scope
        and initialize a new frame by settting offset_cnt to 0
        '''
        if self.in_function:
            raise ValueError("Function declarations cannot be nested.")

        self.in_function = True
        self.push_scope()
        self.offset_cnt = 0

    def exit_function(self):
        self.in_function = False
        self.pop_scope()
        self.offset_cnt = None

    #####################################################################
    # symbol declaration functions

    def declare(self, sym, val):
        # declare symbol in the current scope
        if sym in self.scoped_symtab[CURR_SCOPE]:
            raise ValueError("symbol {} already declared".format(sym))
        # enter the symbol in the current scope
        self.scoped_symtab[CURR_SCOPE][sym] = val

    #####################################################################
    # msic. functions

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

    def get_target_name(self, sym):
        val = self.lookup_sym(sym)
        if val[0] != 'INTEGER':
            raise ValueError("{} is not an integer.".format(sym))
        return val[1]

#########################################################################
# global symtab object

symtab = SymTab()
