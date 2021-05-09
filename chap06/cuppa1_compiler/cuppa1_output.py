'''
This is the output phase of the Cuppa1 compiler

take a list of Exp1bytecode instruction tuples and format them nicely
for output.
'''

#########################################################################
def output(instr_stream):

    output_stream = ''

    for instr in instr_stream:

        if label_def(instr):  # label def - without preceding '\t' or trailing ';'
            output_stream += instr[0] + '\n'

        else:                 # regular instruction - indent and put a ';' at the end
            output_stream += '\t'

            for component in instr:
                output_stream += component + ' '

            output_stream += ';\n'

    return output_stream

#########################################################################
# apply peephole optimization.  The instruction tuple format is:
#   (instr_name_str, [param_str1, param_str2, ...])
def peephole_opt(instr_stream):

    ix = 0
    change = False

    while(True):

        # uncomment the following to see the pattern matcher in action
        #if pattern_fits(3, ix, instr_stream):
        #    print("at ix={}".format(ix))
        #    print(instr_stream[ix])
        #    print(instr_stream[ix+1])
        #    print(instr_stream[ix+2])

        curr_instr = instr_stream[ix]

        ### compute some useful predicates on the current instruction
        is_first_instr = ix == 0
        is_last_instr = ix+1 == len(instr_stream)
        has_label = True if not is_first_instr \
                            and label_def(instr_stream[ix-1]) \
                         else False

        ### our peephole rewrite rules

        # rewrite rule:
        # *L:
        #      noop
        #      <some other instr>
        # =>
        # *L:
        #      <some other instr>
        if pattern_fits(3, ix, instr_stream) \
           and label_def(curr_instr) \
           and relative_instr(1, ix, instr_stream)[0] == 'noop' \
           and not label_def(relative_instr(2, ix, instr_stream)):
             # delete noop
             instr_stream.pop(ix+1)
             change = True
             # uncomment the following to see the pattern matcher in action
             #print("fire rule 1")

        # rewrite rule:
        # * noop
        #   <whatever follows the noop>
        # =>
        # * <whatever follows the noop>
        elif pattern_fits(1, ix, instr_stream) \
             and curr_instr[0] == 'noop' \
             and not has_label:
            instr_stream.pop(ix)
            change = True
             # uncomment the following to see the pattern matcher in action
             #print("fire rule 2")

        # rewrite rule:
        # *L1:
        #    noop
        #  L2:
        # =>
        # *L2:  -- with L1 backpatched to L2 in instr_stream
        elif pattern_fits(3, ix, instr_stream) \
             and label_def(curr_instr) \
             and relative_instr(1, ix, instr_stream)[0] == 'noop' \
             and label_def(relative_instr(2, ix, instr_stream)):
            label1 = get_label_from_def(curr_instr)
            label2 = get_label_from_def(relative_instr(2, ix, instr_stream))
            backpatch_label(label1, label2, instr_stream)
            instr_stream.pop(ix)
            instr_stream.pop(ix)
            change = True
            # uncomment the following to see the pattern matcher in action
            #print("fire rule 3")

        ###  advance ix
        if is_last_instr and not change:
            break

        elif is_last_instr:
            ix = 0
            change = False

        else:
            ix += 1

#########################################################################
def label_def(instr_tuple):

    instr_type = instr_tuple[0]

    if instr_type[-1] == ':':
        return True
    else:
        return False

#########################################################################
def get_label_from_def(instr_tuple):

    if not label_def(instr_tuple):
        raise ValueError("not a label definition: {}".format(instr_tuple))

    instr_type = instr_tuple[0]
    label = instr_type[0:-1] # skip the ending colon
    return label

#########################################################################
def pattern_fits(pattern_size, curr_ix, instr_stream):

    if curr_ix+pattern_size-1 <= len(instr_stream)-1:
        return True
    else:
        return False

#########################################################################
def relative_instr(offset, curr_ix, instr_stream):

    if curr_ix + offset > len(instr_stream)-1:
        raise ValueError("relative instruction index out of bounds: " + str(curr_ix+offset))
    elif curr_ix + offset < 0:
        raise ValueError("relative instruction index out of bounds" + str(curr_ix+offset))
    else:
        return instr_stream[curr_ix+offset]

#########################################################################
def backpatch_label(orig_label, repl_label, instr_stream):

    for ix in range(len(instr_stream)):
        if instr_stream[ix][0] == 'jumpt' and instr_stream[ix][2] == orig_label:
            old_instr = instr_stream.pop(ix)
            new_instr = ('jumpt', old_instr[1], repl_label)
            instr_stream.insert(ix, new_instr)

        elif instr_stream[ix][0] == 'jumpf' and instr_stream[ix][2] == orig_label:
            old_instr = instr_stream.pop(ix)
            new_instr = ('jumpf', old_instr[1], repl_label)
            instr_stream.insert(ix, new_instr)

        elif instr_stream[ix][0] == 'jump' and instr_stream[ix][1] == orig_label:
            instr_stream.pop(ix)
            new_instr = ('jump', repl_label)
            instr_stream.insert(ix, new_instr)

#########################################################################
