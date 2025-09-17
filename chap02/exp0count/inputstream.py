##################################################################
from sys import stdin

class InputStream:
    def __init__(self, char_stream=None):
        # if no stream given read it from the terminal
        if char_stream == None:
            char_stream = stdin.read()
        # turn char stream into a list of characters
        # ignoring any kind of white space
        clean_stream = char_stream.replace(' ','') \
                                  .replace('\t','') \
                                  .replace('\n','') 
        self.stream = [c for c in clean_stream]
        self.stream.append(r'\eof')
        self.stream_ix = 0

    def pointer(self):
        return self.stream[self.stream_ix]

    def next(self):
        if not self.end_of_file():
            self.stream_ix += 1
        return self.pointer()

    def match(self, sym):
        if sym == self.pointer():
            s = self.pointer()
            self.next()
            return s
        else:
            raise SyntaxError('unexpected symbol {} while parsing, expected {}'
                              .format(self.stream[self.stream_ix], sym))

    def end_of_file(self):
        if self.pointer() == r'\eof':
            return True
        else:
            return False
