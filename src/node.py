# Primitive Types
PRIMTYPES = {
    "Int": "int",
    "String": "std::string"
}

# Type includes
INCTYPES = {
    "String": "string"
}

def is_include_needed(lib):
    if lib != "None" and lib.startswith("_"):
        # Include header with .h extension
        if lib.startswith("__"):
            return lib[2:] + ".h"
        return lib[1:]
    return False

def check_for_functions(string):
    string = list(string)
    i = 0
    while i < len(string) - 1:
        if string[i] == ":" and string[i+1] == ":":
            string[i] = ""
            string[i+1] = ""
            i = i - 1
            while string[i].isalpha() or string[i] in ["_", "-"]:
                if string[i] == "_" and string[i+1] != "_" and string[i-1] != "_":
                    string[i] = "std::"
                else:
                    string[i] = ""
                i = i - 1
        i = i + 1
    return "".join(string)


class AssignVar(object):

    def __init__(self, var, type, value):
        self.node = "AssignVar"
        self.var = var
        self.type = type
        self.value = value
        self.inside = True
        self.array = False
        self.codegen = ""
        #self.value = check_for_functions(self.value)

        if self.type.endswith("[]"):
            self.array = True
            self.type = self.type[:-2]
            self.value = list(self.value)
            self.value[0] = "{"
            self.value[len(self.value)-1] = "}"
            new = "".join(self.value)
            self.value = new

    def __str__(self):
        return "AssignVar({var}, {type}, {value})".format(
            var = self.var,
            type = self.type,
            value = self.value
        )

    def __repr__(self):
        return self.__str__()

    def check_include(self):
        if self.type in INCTYPES:
            return INCTYPES[self.type]
        else:
            return False

    def gen_code(self):
        # TODO: Add support for arrays.
        if self.type in PRIMTYPES:
            self.type = PRIMTYPES[self.type]
        if self.array:
            self.codegen = "\tstd::vector<{type}> {name} = {value};\n".format(
                type = self.type,
                name = self.var,
                value = self.value
            )
        else:
            self.codegen = "\t{type} {name} = {value};\n".format(
                type = self.type,
                name = self.var,
                value = self.value
            )
        return self.codegen

class ModVar(object):

    def __init__(self, var, value):
        self.node = "ModVar"
        self.var = var
        self.value = value
        self.inside = True
        self.codegen = ""

    def __str__(self):
        return "ModVar({var}, {value})".format(
            var = self.var,
            value = self.value
        )

    def __repr__(self):
        return self.__str__()

    def check_include(self):
        return False

    def gen_code(self):
        self.codegen = "\t{name} = {value};\n".format(
            name = self.var,
            value = self.value
        )
        return self.codegen

class FuncCall(object):

    def __init__(self, lib, name, args):
        self.node = "FuncCall"
        self.lib = lib
        self.name = name
        self.args = args
        self.inside = True
        self.codegen = ""

    def __str__(self):
        return "FuncCall({lib}, {name}, {args})".format(
            lib = self.lib,
            name = self.name,
            args = self.args
        )

    def __repr__(self):
        return self.__str__()

    def check_include(self):
        return is_include_needed(self.lib)

    def gen_code(self):
        inc = self.check_include()
        if inc != False and not inc.endswith('.h'):
            self.name = "std::" + self.name
        self.codegen = "\t{name}({args});\n".format(
            name = self.name,
            args = self.args
        )
        return self.codegen
