from scanner import Scanner
from parser import Parser
from interpreter import Interpreter

import sys


LEXICAL_EXIT = 1
PARSING_EXIT = 2
RUNTIME_EXIT = 3


class Lox:
    def __init__(self):
        self.has_lexical_error = False
        self.has_parsing_error = False
        self.has_runtime_error = False
        self.interpreter_mode = True
        self.filename = "stdin"
        self.module = "module"
        self.scanner = Scanner(self)
        self.parser = Parser(self)
        self.interpreter = Interpreter(self)

    def run(self, text):
        tokens = self.scanner.tokenize(text)
        ast = self.parser.parse(tokens)
        value = self.interpreter.interpret(ast)
        print("Expression evaluates to: {}".format(value))

    def is_in_interpreter_mode(self):
        return self.interpreter_mode

    def lexical_error(self, error):
        self.has_lexical_error = True
        self.report(error)

    def parsing_error(self, error):
        self.has_parsing_error = True
        self.report(error)

    def runtime_error(self, error):
        self.has_runtime_error = True
        self.report(error)

    def report(self, error):
        print("File <{}>: line {} in <{}>".format(
            self.filename, error.line, self.module
        ))
        if getattr(error, 'token'):
            print("\"Token {}\"".format(error.token.text))
        print("{}: {}".format(
            error.__class__.__name__, error.__str__()
        ))

    def run_file(self, filename):
        self.interpreter_mode = False
        self.filename = filename
        with open(filename, 'r') as f:
            lines = f.readlines()
            code = "".join(lines)
            self.run(code)
            if self.has_lexical_error:
                sys.exit(LEXICAL_EXIT)

            if self.has_parsing_error:
                sys.exit(PARSING_EXIT)

            if self.has_runtime_error:
                sys.exit(RUNTIME_EXIT)

    def run_interpreter(self):
        self.interpreter_mode = True
        while True:
            line = raw_input(">>>")
            self.run(line)

if __name__ == '__main__':
    lox = Lox()
    if len(sys.argv) > 1:
        filename = sys.argv[1]
        print(filename)
        lox.run_file(filename)
    else:
        lox.run_interpreter()
