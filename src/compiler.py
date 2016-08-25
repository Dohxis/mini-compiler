from token import Token

class Program(object):

    def __init__(self, source):
        self.pos = 0
        self.nodes = []
        self.tokens = []
        self.nodes = []
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

        # Strings
        if self.char() == '\"':
            string = ""
            self.incPos()
            while self.char() != '\"':
                string = string + self.char()
                self.incPos()
            return Token("STRING", string)

        # Left paren
        if self.char() == '(':
            return Token("LPAREN", self.char())

        # Right paren
        if self.char() == ')':
            return Token("RPAREN", self.char())

        # Left curly
        if self.char() == '{':
            return Token("LCURLY", self.char())

        # Right curly
        if self.char() == '}':
            return Token("RCURLY", self.char())

        # Left bracket
        if self.char() == '[':
            return Token("LBRACKET", self.char())

        # Right bracket
        if self.char() == ']':
            return Token("RBRACKET", self.char())

        # Colon
        if self.char() == ':':
            return Token("COLON", self.char())

        # Semicolon
        if self.char() == ';':
            return Token("SEMICOLON", self.char())

        # Comma
        if self.char() == ',':
            return Token("COMMA", self.char())

        # Equal
        if self.char() == '=':
            return Token("EQUAL", self.char())

        # Binary operator
        if self.char() in ['+', '-', '/', '*']:
            return Token("BINARYOP", self.char())

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

        print()


def compile(source_file):
    with open(source_file, 'r') as source_file:
        return Program(source_file.read())
