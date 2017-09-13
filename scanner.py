from tokens import Types, Token, single_char_types, \
                   one_two_char_types, reserved_kw_types

EOF = '\0'


class LexicalError(Exception):
    def __init__(self, msg, line):
        super(LexicalError, self).__init__(msg, line)
        self.token = None
        self.line = line
        self.msg = msg


class Scanner:
    def __init__(self, lox):
        self.current = 0
        self.line = 1
        self.tokens = []
        self.lox = lox

    def is_at_end(self):
        return self.current > len(self.text) - 1

    def get_token(self, text, ttype, value=None):
        return Token(text, ttype, self.line, value)

    def peek(self):
        if self.current < len(self.text) - 1:
            return self.text[self.current + 1]
        else:
            return EOF

    def check(self, char):
        return self.peek() == char

    def match(self, *chars):
        return self.current_char in chars

    def reset(self):
        self.current = 0
        self.line = 1
        self.tokens = []

    def advance(self):
        char = self.current_char

        if self.current < len(self.text) - 1:
            self.current += 1
            self.current_char = self.text[self.current]
            if self.current_char == '\n':
                self.line += 1
        elif self.current == len(self.text) - 1:
            self.current += 1
            self.current_char = EOF

        return char

    def advance_to_nonspace(self):
        while self.current_char.isspace():
            self.advance()
        return self.current_char

    def get_string(self):
        quote_mark = self.advance()
        s = ""
        while not self.match(quote_mark, EOF):
            s += self.advance()

        # Need to allow for escape characters
        if self.match(quote_mark):
            self.advance()
            return self.get_token(s, Types.STRING, s)
        else:
            raise LexicalError("Unterminated string", self.line)

    def get_number(self):
        number = self.advance()
        while self.current_char.isdigit():
            # Concatenate to number string as long as we find digits
            number += self.advance()

        if self.match('.'):
            # If the first nondigit is a '.' then we have a floating point
            number += self.advance()
            while self.current_char.isdigit():
                number += self.advance()

        # If the nondigit is a space or EOF, then we return the token
        if self.current_char.isspace() or self.is_at_end() \
            or self.current_char in single_char_types.keys() or \
                self.current_char in one_two_char_types.keys():
            return self.get_token(number, Types.NUMBER, float(number))

        # Otherwise this is an invalid number so we raise a lexical error
        raise LexicalError(
            "Invalid numeric character", self.line
        )

    def get_alphanumeric(self):
        s = self.advance()
        while self.current_char.isalpha() or \
            self.current_char.isdigit():
            # Note, don't need EOF check since "\0" is not alphanumeric
            s += self.advance()

        if s in reserved_kw_types:
            type_key = reserved_kw_types.get(s)
            ttype = getattr(Types, type_key)
            return self.get_token(s, ttype)

        return self.get_token(s, Types.IDENTIFIER, s)

    def get_next_token(self):
        self.advance_to_nonspace()

        char = self.current_char
        result = ""
        type_map = one_two_char_types

        if char.isdigit():
            return self.get_number()

        if char.isalpha():
            return self.get_alphanumeric()

        if char in ("\"", "\'"):
            return self.get_string()

        elif char in single_char_types:
            result = char
            type_map = single_char_types

        elif char in one_two_char_types:
            result = char + self.advance() if self.check('=') else char

        elif char == "&" and self.check("&"):
            result = char + self.advance()

        elif char == "|" and self.check("|"):
            result = char + self.advance()

        else:
            raise LexicalError(
                "Invalid character {}".format(self.current_char),
                self.line)

        type_key = type_map.get(result)
        ttype = getattr(Types, type_key)
        self.advance()
        return self.get_token(result, ttype)

    def tokenize(self, text):
        self.reset()
        self.text = text
        self.current_char = self.text[0]
        try:
            while self.current < len(self.text):
                token = self.get_next_token()
                self.tokens.append(token)
            return self.tokens
        except LexicalError as error:
            self.lox.lexical_error(error)
