import unittest
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))

from interpreter.scanner import Scanner
from interpreter.parser import Parser
from interpreter.lox import Lox


EXPRESSION = "var a = 2 + 3;\nvar b = 3 + 4;\n if (a > 3 && b < 10) {print a; print b;}"

class TestLox(unittest.TestCase):

    @classmethod
    def setUp(cls):
        cls.expression = EXPRESSION
        cls.lox = Lox()
        cls.scanner = cls.lox.scanner
        cls.parser = cls.lox.parser

    def test_lexer_tokenize(self):
        self.scanner.tokenize(self.expression)
        tokens = self.scanner.tokens
        for t in tokens:
            print(t)

    def test_parser_parse(self):
        self.scanner.tokenize(self.expression)
        tokens = self.scanner.tokens
        ast = self.parser.parse(tokens)
        print(ast)

    def test_interpreter_run(self):
        self.lox.run(self.expression)


if __name__ == '__main__':
    unittest.main()
