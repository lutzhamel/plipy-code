'''
codegen

this is the static code generator for our Cuppa1 compiler based
on the LLVM backend
'''

#########################################################################
# llvm stuff
#########################################################################

from llvmlite import ir
from llvmlite import binding

# set the following to the target machine
target_triple = binding.get_default_triple()
# For cross-compilation replace the default target triple above
# with the desired target triple, e.g.
#   target_triple = "x86_64-unknown-linux-gnu"

# IR entities needed throughout the code generator
# these are initialized in make_ir
main = None
module = None
builder = None
printf = None
scanf = None
print_fmt = None
scan_fmt = None
prompt_fmt = None

# variable address hash - we have to keep track
# of the variable-address pairs we have generated in the IR
# in order to avoid creating multiple instances of the same global vars.
addresses = dict()

# define types that we will commonly use
i64 = ir.IntType(64);
voidptr = ir.IntType(64).as_pointer()
io_fun = ir.FunctionType(i64, [voidptr], var_arg=True)

# often used constants
i64_const0 = ir.Constant(i64, 0)
i64_const1 = ir.Constant(i64, 1)

#########################################################################
# node functions
#########################################################################
def stmtlst(node):

    (STMTLIST, lst) = node

    for stmt in lst:
        walk(stmt)

#########################################################################
def nil(node):

    (NIL,) = node

#########################################################################
def assign_stmt(node):

    (ASSIGN, (ID, id), exp) = node

    exp_val = walk(exp)

    try:
        id_addr = addresses[id]
    except KeyError:
        # compute an address for id
        id_addr = ir.GlobalVariable(module, i64, name=id)
        id_addr.global_constant = False
        id_addr.initializer = i64_const0
        addresses[id] = id_addr

    builder.store(exp_val, id_addr)

#########################################################################
def get_stmt(node):

    (GET, (ID, id)) = node

    try:
        id_addr = addresses[id]
    except KeyError:
        # compute an address for id
        id_addr = ir.GlobalVariable(module, i64, name=id)
        id_addr.global_constant = False
        id_addr.initializer = i64_const0
        addresses[id] = id_addr

    builder.call(printf, [prompt_fmt])
    builder.call(scanf, [scan_fmt, id_addr])

#########################################################################
def put_stmt(node):

    (PUT, exp) = node

    exp_val = walk(exp)
    builder.call(printf, [print_fmt, exp_val])

#########################################################################
def while_stmt(node):
    # the code here was inspired by the Python implementation of
    # the Kaleidoscope compiler:
    #      https://github.com/symhom/Kaleidoscope_Compiler

    (WHILE, cond, body) = node

    w_body_block = builder.append_basic_block("w_body")
    w_after_block = builder.append_basic_block("w_after")

    # head
    cond_val = walk(cond)
    cmp_val = builder.icmp_signed('!=', cond_val, i64_const0)
    builder.cbranch(cmp_val, w_body_block, w_after_block)

    # body
    builder.position_at_start(w_body_block)
    walk(body)
    cond_val = walk(cond)
    cmp_val = builder.icmp_signed('!=', cond_val, i64_const0)
    builder.cbranch(cmp_val, w_body_block, w_after_block)

    # after
    builder.position_at_start(w_after_block)

#########################################################################
def if_stmt(node):

    (IF, cond, then_stmt, else_stmt) = node

    cond_val = walk(cond)
    cmp_val = builder.icmp_signed('!=', cond_val, i64_const0)

    if else_stmt[0] == 'NIL':
        with builder.if_then(cmp_val):
            walk(then_stmt)
    else:
        with builder.if_else(cmp_val) as (then, otherwise):
            with then:
                walk(then_stmt)
            with otherwise:
                walk(else_stmt)

#########################################################################
def block_stmt(node):

    (BLOCK, s) = node
    walk(s)

#########################################################################
def binop_exp(node):

    (OP, lc, rc) = node

    l_val = walk(lc)
    r_val = walk(rc)

    if OP == 'PLUS':
        return builder.add(l_val, r_val)
    elif OP == 'MINUS':
        return builder.sub(l_val, r_val)
    elif OP == 'MUL':
        return builder.mul(l_val, r_val)
    elif OP == 'DIV':
        return builder.sdiv(l_val, r_val)
    elif OP == 'EQ':
        return builder.icmp_signed('==', l_val, r_val)
    elif OP == 'LE':
        return builder.icmp_signed('<=', l_val, r_val)
    else:
        raise ValueError('internal error')

#########################################################################
def integer_exp(node):

    (INTEGER, value) = node

    const_val = ir.Constant(i64, int(value))
    return const_val

#########################################################################
def id_exp(node):

    (ID, id) = node

    try:
        id_addr = addresses[id]
    except KeyError:
        # compute an address for id
        id_addr = ir.GlobalVariable(module, i64, name=id)
        id_addr.global_constant = False
        id_addr.initializer = i64_const0
        addresses[id] = id_addr

    id_val = builder.load(id_addr)

    return id_val

#########################################################################
def uminus_exp(node):

    (UMINUS, e) = node

    e_val = walk(e)
    return builder.neg(e_val)

#########################################################################
def not_exp(node):

    (NOT, e) = node

    e_val = walk(e)

    return builder.not_(e_val)

#########################################################################
def paren_exp(node):

    (PAREN, exp) = node

    exp_val = walk(exp)

    return exp_val

#########################################################################
# walk
#########################################################################
def walk(node):
    node_type = node[0]

    if node_type in dispatch:
        node_function = dispatch[node_type]
        return node_function(node)
    else:
        raise ValueError("walk: unknown tree node type: " + node_type)

# a dictionary to associate tree nodes with node functions
dispatch = {
    'STMTLIST'  : stmtlst,
    'NIL'      : nil,
    'ASSIGN'   : assign_stmt,
    'GET'      : get_stmt,
    'PUT'      : put_stmt,
    'WHILE'    : while_stmt,
    'IF'       : if_stmt,
    'BLOCK'    : block_stmt,
    'INTEGER'  : integer_exp,
    'ID'       : id_exp,
    'UMINUS'   : uminus_exp,
    'NOT'      : not_exp,
    'PAREN'    : paren_exp,
    'PLUS'     : binop_exp,
    'MINUS'    : binop_exp,
    'MUL'      : binop_exp,
    'DIV'      : binop_exp,
    'EQ'       : binop_exp,
    'LE'       : binop_exp,
}

#########################################################################
# make a global string variable - declares a global string var in
# current IR context

def make_str_var(name, init):
    initializer = init+"\0" # zero terminated!
    constant_val = ir.Constant(ir.ArrayType(ir.IntType(8), len(initializer)),
                        bytearray(initializer.encode("utf8")))
    global_str = ir.GlobalVariable(module, constant_val.type, name=name)
    global_str.global_constant = True
    global_str.initializer = constant_val
    return global_str

#########################################################################
# make_ir

def make_ir(ast):
    global main
    global module
    global builder
    global printf
    global scanf
    global print_fmt
    global scan_fmt
    global prompt_fmt

    # define the module and the target machine for our code
    module = ir.Module(name="main")
    module.triple = target_triple

    # we have to embed our code in a main function
    # in order to use the C runtime system
    main_type = ir.FunctionType(ir.VoidType(), [])
    main = ir.Function(module, main_type, name="main")

    # I/O RTS functions
    printf = ir.Function(module, io_fun, name="printf")
    scanf = ir.Function(module, io_fun, name="scanf")

    # all our Cuppa1 code will start in this block
    block = main.append_basic_block(name="entry")
    builder = ir.IRBuilder(block)

    # string variable to hold the format string for printf
    print_fmt_string = make_str_var("pfmtstr", "%d\n")
    print_fmt = builder.bitcast(print_fmt_string, voidptr)

    # string variable to hold the format string for scanf
    scan_fmt_string = make_str_var("sfmtstr", "%lld")
    scan_fmt = builder.bitcast(scan_fmt_string, voidptr)

    # string variable to hold the format string for prompt
    prompt_fmt_string = make_str_var("qfmtstr", "? ")
    prompt_fmt = builder.bitcast(prompt_fmt_string, voidptr)

    # generate code for the program
    walk(ast)

    # We have to emit some sort of block terminator
    builder.ret_void()

    # return the IR module as a string
    return str(module)

#########################################################################
# make_asm

def make_asm(ir_module):

    # Note: llvmlite does not allow us to do cross-compilation
    # only native compilation is supported.
    # therefore, only use default triple for native code generation

    binding.initialize()
    binding.initialize_native_target()
    binding.initialize_native_asmprinter()
    target = binding.Target.from_triple(binding.get_default_triple())
    target_machine = target.create_target_machine()
    target_machine.set_asm_verbosity(True)

    # necessary in order to generate code from ir module
    mod_ref = binding.parse_assembly(ir_module)
    mod_ref.verify()

    # generate the native assembly code
    asm_code = target_machine.emit_assembly(mod_ref)

    # return asm code as a string
    return asm_code

#########################################################################
# codegen

def codegen(ast, ir_flag=False):

    ir_module = make_ir(ast)
    if ir_flag:
        return ir_module
    else:
        if binding.get_default_triple() != target_triple:
            raise ValueError('cross-compilation not supported in code generator')
        asm = make_asm(ir_module)
        return asm
