# define and initialize the structures of our abstract machine

class State:

    def __init__(self):
        self.initialize()

    def initialize(self):
        self.program = []
        self.symbol_table = dict()
        self.label_table = dict()
        self.instr_ix = 0

state = State()
