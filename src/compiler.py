class Program:

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
        return None;

    def init(self):
        while self.pos < len(self.source):
            self.tokens.append(self.tokenize())
            print(self.tokenize())
            self.incPos()

def compile(source_file):
    with open(source_file, 'r') as source_file:
        return Program(source_file.read())
