from token import Token

class Program(object):

    def __init__(self, source):
        self.pos = 0
        self.nodes = []
        self.tokens = []
        self.source = source
        self.init()

    def char(self):
        return self.source[self.pos]

    def incPos(self):
        self.pos = self.pos + 1

    def peek(self, far=1):
        return self.source[self.pos + far]

    def tokenize(self):

        # Definitions
        if self.char().isalpha():
            definition = self.char()
            while self.peek().isalpha():
                definition = definition + self.peek()
                self.incPos()
            return Token("DEFINITION", definition)

        if self.char().isspace():
            return None

        return Token("UNKOWN", self.char())

    def init(self):
        while self.pos < len(self.source):
            token = self.tokenize()
            if token != None:
                self.tokens.append(token)
                print(token)
            self.incPos()

def compile(source_file):
    with open(source_file, 'r') as source_file:
        return Program(source_file.read())
