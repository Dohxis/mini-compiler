# Primitive Types
PRIMTYPES = {
    "Int": "int",
    "String": "std::string",
    "Float": "double",
    "Bool": "bool",
    "UInt": "unsigned int",
    "size_t": "size_t"
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
        # --SliceStart--
        tempType = list(self.type)
        if tempType[0] == ":":
            tempType[0] = ""
        tempType = "".join(tempType).split("=")
        if tempType.__len__() == 2:
            self.value = tempType[1]
        self.type = tempType[0]
        # --SliceEnd--
        if self.value != None:
            self.value, self.libs = check_for_functions(self.value)
        else:
            self.libs = []
        if self.type.endswith("[]"):
            self.array = True
            self.type = self.type[:-2]
            if self.value is not None:
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
        if self.value == None:
            # TODO: Add support for arrays.
            if self.type in PRIMTYPES:
                self.type = PRIMTYPES[self.type]
            if self.array:
                self.codegen = "\tstd::vector<{type}> {name};\n".format(
                    type = self.type,
                    name = self.var,
                )
            else:
                self.codegen = "\t{type} {name};\n".format(
                    type = self.type,
                    name = self.var,
                )
        else:
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
        self.node = "FuncDefine"
        self.name = name
        self.args = self.convert_args(args)
        self.type = self.prime(self.vector_check(self.get_type(args)))
        self.inside = False
        self.codegen = ""
        self.libs = []

    def check_include(self):
        pass

    def prime(self, temp):
        if temp in PRIMTYPES:
            return PRIMTYPES[temp]
        return temp

    def __str__(self):
        return "FuncDefine({name}, {args}):{type}".format(
            name = self.name,
            args = self.args,
            type = self.type
        )

    def __repr__(self):
        return self.__str__()

    def get_type(self, args):
        args = args.rstrip()
        if args[-1:] == ")":
            return "void"
        else:
            listargs = list(args)
            pos = listargs.__len__() - 1
            typeT = []
            while pos > 0:
                typeT.append(listargs[pos])
                pos -= 1
                if listargs[pos] == ":":
                    return "".join(list(reversed(typeT)))

    def convert_args(self, args):
        listargs = list(args)
        pos = listargs.__len__() - 1
        while pos > 0:
            if listargs[pos] == ")":
                listargs[pos] = ""
                pos = 0
            listargs[pos] = ""
            pos -= 1
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

    def include_libs(self, type):
        typeR = type.rstrip()
        if typeR.startswith("String"):
            self.libs.append("string")
        if typeR.endswith("[]"):
            self.libs.append("vector")

    def vector_check(self, typeR):
        typeF = typeR.rstrip()
        if typeF.endswith("[]"):
            typeF = self.prime(typeF[:-2])
            return "std::vector<{type}>".format(
                type=typeF
            )
        return typeF

    def gen_code(self, lib=False):
        self.codegen = "{type} {name}(".format(
            type=self.type,
            name=self.name
        )
        pos = 0
        while pos < self.args.__len__():
            if self.args[pos] != "":
                k = self.args[pos].split(':')
                arr = [k[0]] + [l for l in k[1:]]
                self.include_libs(arr[1])
                arr[1] = self.vector_check(arr[1])
                arr[1] = self.prime(arr[1])
                if not lib:
                    self.codegen += "{type} {name}".format(
                        type=arr[1],
                        name=arr[0]
                    )
                else:
                    self.codegen += "{type}".format(
                        type=arr[1],
                        name=arr[0]
                    )
            pos += 1
            if pos != self.args.__len__():
                self.codegen += ", "
            else:
                if not lib:
                    self.codegen += "){\n"
                else:
                    self.codegen += ");\n"
        return self.codegen

class FuncReturn(object):
    def __init__(self, args):
        self.codegen = ""
        self.libs = []
        self.node = "return"
        self.inside = True
        self.args = args

    def gen_code(self):
        self.codegen = "\treturn {args};\n".format(
            args=self.args
        )
        return self.codegen

    def check_include(self):
        pass

class End(object):
    def __init__(self):
        self.codegen = ""
        self.libs = []
        self.node = "End"
        self.inside = True
        self.addSemi = False

    def gen_code(self):
        self.codegen = "}"
        if self.addSemi:
            self.codegen += ";"
        self.codegen += "\n"
        return self.codegen

    def check_include(self):
        pass

class IfClause(object):
    def __init__(self, args, name):
        self.node = "IfClause"
        self.args = args
        self.name = name
        self.inside = True
        self.codegen = ""
        self.libs = []

    def check_include(self):
        pass

    def __str__(self):
        return "IfClause({args})".format(
            args=self.args,
        )

    def __repr__(self):
        return self.__str__()

    def gen_code(self):
        args1, _ = check_for_functions(self.args)
        self.codegen = "\t{name}{args}".format(
            args = args1,
            name=self.name
        )
        self.codegen += "{\n"
        return self.codegen

class ForStmt(object):

    def __init__(self, var, args):
        self.node = "ForStmt"
        self.var = var
        self.args = args.split("in")
        args2 = self.args[1].split(";")
        self.args = [self.args[0]] + args2[0].split("..") + args2[1:]
        self.inside = True
        self.codegen = ""
        self.libs = []

    def __str__(self):
        return "ForStmt({var}, {args})".format(
            var = self.var,
            args = self.args
        )

    def __repr__(self):
        return self.__str__()

    def check_include(self):
        pass

    def gen_code(self):

        vartype = "int"
        varname = var = self.var
        varstart = self.args[1]
        varend = self.args[2]
        if varstart < varend:
            comparator = "<"
        else:
            comparator = ">"
        increment_by = "1"

        if len(self.args) >= 4:
            if self.args[3].isdigit():
                vartype = "int"
                increment_by = self.args[3]
            elif "." in self.args[3]:
                vartype = "double"
                increment_by = self.args[3]
            else:
                comparator = self.args[3]

        if len(self.args) == 5:
            if self.args[4].isdigit():
                vartype = "int"
                increment_by = self.args[4]
            elif "." in self.args[4]:
                vartype = "double"
                increment_by = self.args[4]
            else:
                comparator = self.args[4]

        self.codegen = "for ({type} {var} = {start}; {var} {compare} {end}; {var} += {increment}) ".format(
            type = vartype,
            var = self.var,
            start = varstart,
            compare = comparator,
            end = varend,
            increment = increment_by
        )

        self.codegen += "{\n"
        return self.codegen

class StructStmt(object):

    def __init__(self, name):
        self.node = "StructStmt"
        self.name = name
        self.inside = False
        self.codegen = ""
        self.libs = []

    def __str__(self):
        return "StructStmt({name})".format(
            name = self.name
        )

    def __repr__(self):
        return self.__str__()

    def check_include(self):
        pass

    def gen_code(self):
        self.codegen = "struct {name} ".format(
            name = self.name
        )
        self.codegen += "{"
        return self.codegen

class WhileStmt(object):

        def __init__(self, args):
            self.node = "ForStmt"
            self.args = args
            self.inside = True
            self.codegen = ""
            self.libs = []

        def __str__(self):
            return "ForStmt({args})".format(
                args = self.args
            )

        def __repr__(self):
            return self.__str__()

        def check_include(self):
            pass

        def gen_code(self):
            self.codegen += "while ({args})".format(
                args = self.args
            )
            self.codegen += "{\n"
            return self.codegen
