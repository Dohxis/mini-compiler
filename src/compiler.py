from token import Token
from node import *
import os

class Program(object):

    def __init__(self, source, name):
        self.name = name
        self.pos = 0
        self.posN = 0
        self.nodes = []
        self.tokens = []
        self.nodes = []
        self.source = source
        self.init()

    def char(self):
        return self.source[self.pos]

    def incPos(self):
        self.pos = self.pos + 1

    def incPosN(self):
        self.posN = self.posN + 1

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

        # Integers
        if self.char().isnumeric():
            integer = self.char()
            while self.peek().isnumeric():
                integer = integer + self.peek()
                self.incPos()
            return Token("INTEGER", integer)

        # Strings
        if self.char() == '\"':
            string = "\""
            self.incPos()
            while self.char() != '\"':
                string = string + self.char()
                self.incPos()
            return Token("STRING", string + "\"")

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

    def peekNode(self, far=1):
        return self.tokens[self.posN + far]

    def node(self):
        return self.tokens[self.posN]

    def eat_type(self):
        self.incPosN()
        type = ""
        while self.node().type != "EQUAL":
            type = type + self.node().value
            self.incPosN()
        return type

    def eat_value(self):
        value = ""
        while self.node().type != "SEMICOLON":
            value = value + self.node().value
            self.incPosN()
        return value


    def makeNode(self):

        # AssignVar
        # TODO: This was a fast hack to check if we are dealing with variables or function arguments.
        # We need a better way to check this kind of action
        if(self.node().type == "DEFINITION" and self.peekNode().type == "COLON" and (self.peekNode(3).type == "EQUAL" or self.peekNode(5).type == "EQUAL")):
            # name
            name = self.node().value
            self.incPosN()
            # type
            type = self.eat_type()
            # value
            self.incPosN()
            value = self.eat_value()

            return AssignVar(name, type, value)

        # ModVar
        if(self.node().type == "DEFINITION" and self.peekNode().type == "EQUAL"):
            #name
            name = self.node().value
            self.incPosN()
            #value
            self.incPosN()
            value = self.eat_value()

            return ModVar(name, value)


    def compile_to_cpp(self):

        INCLUDED = []

        with open((self.name + ".cpp"), "w") as output:
                # includes goes here
                for _i, node in enumerate(self.nodes):
                    inc = node.check_include()
                    if inc is not False and inc not in INCLUDED:
                        output.write("#include<"+ inc +">\n")


                output.write("\nint main() {\n")

                # code goes here expect of new functions and imports
                # node.inside is a boolean which says if the node has
                # to be compiled inside the main function
                for _i, node in enumerate(self.nodes):
                    if node.inside:
                        output.write(node.gen_code())

                output.write("\treturn 0;\n")
                output.write("}\n")

        os.system("cat " + self.name + ".cpp")
        os.system("g++ " + self.name + ".cpp" + " -o " + self.name)

    def init(self):
        while self.pos < len(self.source):
            token = self.tokenize()
            if token != None:
                self.tokens.append(token)
                print(token)
            self.incPos()

        print()

        while self.posN < len(self.tokens):
            node = self.makeNode()
            if node != None:
                self.nodes.append(node)
                print(node)
            self.incPosN()

        print()

        self.compile_to_cpp()


def compile(source_file):
    name = os.path.splitext(source_file)[0]
    with open(source_file, 'r') as source_file:
        return Program(source_file.read(), name)
