# Primitive Types
PRIMTYPES = {
    "Int": "int",
    "String": "std::string",
    "Float": "double"
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
    libs = []
    string = list(string)
    i = 0
    while i < len(string) - 1:
        lib = []
        if string[i] == ":" and string[i+1] == ":":
            x = i - 1
            while string[x].isalpha() or string[x] in ["_", "-"]:
                if string[x] == "_":
                    if string[x-1] == "_":
                        c = x - 1       # if "__" is found, deletes everything from the first "_"
                    else:               # otherwise, changes "_" to "std::" and deletes everything after that
                        string[x] = "std::"
                        c = x + 1
                    while not(string[c] == ":" and string[c+1] != ":"):  # deletes until the last ":" is reached
                        if string[c] != ":":
                            lib.append(string[c])  # Takes in chars of the soon to be deleted lib names
                        string[c] = ""
                        c += 1
                    string[c] = ""  # finally, the last ":" is deleted
                x -= 1
        if lib.__len__() != 0:
            libs.append("".join(lib))  # joins the saved chars to create a string of the lib name
        i += 1
    libs = convert_libs(libs)  # the saved libs are converted to cpp format
    return "".join(string), libs


def convert_libs(libs):  # coverts library names to cpp format
    newlibs = []
    for lib in libs:
        if lib[:1] == "_":
            newlibs.append(lib[2:] + ".h")  # example: "__cmath" is converted to "cmath.h"
        else:
            newlibs.append(lib)  # example: "_cmath" is converted to "cmath"
    '''
    Side note: Due to the way check_for_functions() works, it fetches "cmath"
    instead of "_cmath" in the first place
    '''
    return newlibs


class AssignVar(object):

    def __init__(self, var, type, value):
        self.node = "AssignVar"
        self.var = var
        self.type = type
        self.value = value
        self.inside = True
        self.array = False
        self.codegen = ""
        self.value, self.libs = check_for_functions(self.value)

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
            self.libs.append(INCTYPES[self.type])

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
        self.value, self.libs = check_for_functions(self.value)

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
        self.libs = []
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
        inc = is_include_needed(self.lib)
        if inc != False:
            self.libs.append(inc)
        return inc

    def gen_code(self):
        inc = self.check_include()
        if inc != False and not inc.endswith('.h'):
            self.name = "std::" + self.name
        self.codegen = "\t{name}({args});\n".format(
            name = self.name,
            args = self.args
        )
        return self.codegen


class FuncDefine(object):
    def __init__(self, name, args):
        self.node = "FuncCall"
        self.name = name
        self.args = self.convert_args(args)
        self.type = self.get_type(args)
        self.inside = False
        self.codegen = ""
        self.libs = []

    def check_include(self):
        pass

    def __str__(self):
        return "FuncDefine({name}, {args})".format(
            name = self.name,
            args = self.args
        )

    def __repr__(self):
        return self.__str__()

    def get_type(self, args):
        if self.args[-1:] == ")":
            return "void"
        else:
            listargs = list(args)
            pos = listargs.__len__() - 1
            typeT = []
            while pos > 0:
                typeT.append(listargs[pos])
                pos -= 1
                if listargs[pos] == ":":
                    return "".join(list(reversed(typeT))).lower()

    def convert_args(self, args):
        listargs = list(args)
        pos = listargs.__len__() - 1
        while pos > 0:
            listargs[pos] = ""
            pos -= 1
            if listargs[pos] == ")":
                listargs[pos] = ""
                pos = 0
        pos = 1
        temparg = []
        args1 = []
        while pos < listargs.__len__():
            if listargs[pos] != " ":
                if listargs[pos] != "(":
                    if listargs[pos] != ",":
                        args1.append(listargs[pos])
                    else:
                        temparg.append("".join(args1))
                        args1 = []
            pos += 1
        temparg.append("".join(args1))
        return temparg


    def gen_code(self):
        self.codegen = "{type} {name}(".format(
            type=self.type,
            name=self.name
        )
        pos = 0
        while pos < self.args.__len__():
            k = self.args[pos].split(':')
            arr = [k[0]] + [l for l in k[1:]]
            self.codegen += "{type} {name}".format(
                type=arr[1],
                name=arr[0]
            )
            pos += 1
            if pos != self.args.__len__():
                self.codegen += ", "
            else:
                self.codegen += "){\n"
        return self.codegen

class End(object):
    def __init__(self):
        self.codegen = ""

    def gen_code(self):
        self.codegen = "}"
