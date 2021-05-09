from cuppa2_symtab import SymTab

class State:
    def __init__(self):
        self.initialize()

    def initialize(self):
        # symbol table to hold variable-value associations
        self.symbol_table = SymTab()

state = State()
