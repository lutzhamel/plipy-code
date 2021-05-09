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
            output_stream += '\t' + instr[0] + ' ' + instr[1] + '\n'

        else:                 # regular instruction - indent and put a ';' at the end
            output_stream += '\t'

            for i in range(len(instr)):
                output_stream += instr[i]
                if len(instr) == 1:
                    output_stream += '\n'
                elif i == 0:
                    output_stream += '\t'
                elif i < len(instr)-1:
                    output_stream += ', '
                else:
                    output_stream += '\n'

    return output_stream

#########################################################################
def label_def(instr_tuple):

    instr_name = instr_tuple[0]

    if instr_name[-1] == ':':
        return True
    else:
        return False

#########################################################################
def output_data(data_tuples):
    data_stream = '\t.data\n'
    for (name, size) in data_tuples:
        data_stream += "\t.lcomm {}, {}\n".format(name,size)
    data_stream += "\n"

    return data_stream

#########################################################################
