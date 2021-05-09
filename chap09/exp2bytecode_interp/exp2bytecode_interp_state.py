# define and initialize the structures of our abstract machine

class State:

    def __init__(self):
        self.initialize()

    def initialize(self):
        self.program = list()
        self.symbol_table = dict()
        self.label_table = dict()
        self.runtime_stack = list()
        self.instr_ix = 0
        self.rvx = None # return value register

state = State()
