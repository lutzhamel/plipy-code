# This is the output phase of the Cuppa3 compiler

# take a list of Exp2bytecode instruction tuples and format them nicely
# for output. 

#########################################################################
def output(instr_stream):

    output_stream = ''
    
    for instr in instr_stream:

        if label_def(instr):  # label def - print without preceeding '\t' or trailing ';'
            output_stream += instr[0] + '\n'
        
        elif instr[0] == '#': # comment dummy instruction
            output_stream += instr[0] + ' ' + instr[1] + '\n'

        else:                 # regular instruction - indent and put a ';' at the end
            output_stream += '\t'
                
            for component in instr:
                output_stream += component + ' '

            output_stream += ';\n'

    return output_stream

#########################################################################
def label_def(instr_tuple):
    
    instr_name = instr_tuple[0]
    
    if instr_name[-1] == ':':
        return True
    else:
        return False

#########################################################################
