'''
Python does not allow pattern matching on literals.
This function aids with that.
'''

def assert_match(input, expected):
    if input != expected:
        raise ValueError("Pattern match failed: expected {} but got {}".format(expected, input))
