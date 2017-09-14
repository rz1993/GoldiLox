def enum(name, *args, **kwargs):
    """ Helper method for creating a class grouping of constants """
    enums = dict(zip(args, range(len(args))), **kwargs)
    return type(name, (), enums)

Types = enum(
    'TokenTypes',
    #End of file
    'EOF',

    # Single character tokens
    'LPAREN', 'RPAREN', 'LBRACE', 'RBRACE', 'PLUS', 'MINUS',
    'COMMA', 'DOT', 'SEMICOLON', 'SLASH', 'STAR',

    # One or two character token types
    'BANG', 'BANG_EQUAL',
    'EQUAL', 'EQUAL_EQUAL',
    'GT', 'GTE', 'LT', 'LTE',
    'LOGIC_AND', 'LOGIC_OR',

    # Literal types
    'IDENTIFIER', 'STRING', 'NUMBER',

    # Keywords
    'AND', 'CLASS', 'ELSE', 'FALSE', 'FUN', 'IF', 'NIL',
    'OR', 'PRINT', 'RETURN', 'SUPER', 'TRUE', 'VAR', 'WHILE',
    'FOR'
)

single_char_types = {
    '(': 'LPAREN', ')': 'RPAREN', '{': 'LBRACE', '}': 'RBRACE',
    '+': 'PLUS', '-': 'MINUS', ',': 'COMMA', '.': 'DOT',
    ';': 'SEMICOLON', '/': 'SLASH', '*': 'STAR', "\x00": 'EOF'
}

one_two_char_types = {
    '!': 'BANG', '!=': 'BANG_EQUAL', '=': 'EQUAL', '==': 'EQUAL_EQUAL',
    '>': 'GT', '>=': 'GTE', '<': 'LT', '<=': 'LTE', '&&': 'LOGIC_AND',
    '||': 'LOGIC_OR'
}

reserved_kw_types = {
    'and': 'AND', 'class': 'CLASS', 'else': 'ELSE',
    'False': 'FALSE', 'fun': 'FUN', 'if': 'IF',
    'nil': 'NIL', 'or': 'OR', 'print': 'PRINT',
    'return': 'RETURN', 'super': 'SUPER', 'True': 'TRUE',
    'var': 'VAR', 'while': 'WHILE', 'for': 'FOR'
}

class Token:
    def __init__(self, text, typespec, line, value=None):
        self.value = value
        self.type = typespec
        self.line = line
        self.text = text

    def __str__(self):
        return "Token type: {}, text: {}, line: {}".format(
            self.type, self.text, self.line
        )
