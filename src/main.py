import sys
import os.path
import compiler

def getFileToCompile():
    if len(sys.argv) < 2:
        print("Usage: compile [main.fr]")
        sys.exit()

    if not sys.argv[1].endswith(".fr"):
        print("Source file's extension must be '.fr'")
        sys.exit()

    if not os.path.isfile(sys.argv[1]):
        print("Cannot find " + sys.argv[1])
        sys.exit()

    return sys.argv[1]


if __name__ == "__main__":
    newArgs = sys.argv[2:]
    file = getFileToCompile()
    compiler.compile(file, newArgs)
