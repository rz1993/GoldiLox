import tokens

class Lexer:
    def __init__(self):
        self.text = ""
        self.current_pos = 0
        self.current_char = self.text[0]
        self.line = 1

    def reset(self):
        self.current_pos = 0
        self.current_char = self.text[0]
        self.line = 1

    def peek(self):
        peek_pos = self.current_pos + 1
        if peek_pos > len(self.text) - 1:
            return tokens.EOF
        else:
            return self.text[peek_pos]

    def advance(self):
        if self.current_pos < len(self.text) - 1:
            self.current_pos += 1
            self.current_char = self.text[self.current_pos]
            return self.current_char
        self.current_char = tokens.EOF
        return self.current_char

    def advance_to_nonspace(self):
        while self.current_char != tokens.EOF and \
            self.current_char.isspace():
            if self.current_char == '\n':
                self.line += 1
            self.advance()
        return self.current_char

    def get_num(self):
        result = ""
        while self.current_char.isdigit():
            result = result + self.current_char
            self.advance()

        if self.current_char == '.':
            result = result + self.current_char
            self.advance()
            while self.current_char.isdigit():
                result = result + self.current_char
                self.advance()

        return tokens.Token(float(result), tokens.NUMBER, self.line)

    def get_alpha(self):
        result = ""
        while self.current_char and self.current_char.isalpha():
            result = result + self.current_char
            self.advance()

        return result

    def get_var(self):
        result = self.get_alpha()
        if result in tokens.RESERVED_KW:
            token = tokens.RESERVED_KW.get(result)
        else:
            token = tokens.Token(result, tokens.VAR, self.line)

        return token

    def get_next_token(self):
        self.advance_to_nonspace()
        char = self.current_char
        if char.isdigit():
            return self.get_num()

        elif char.isalpha():
            return self.get_var()

        elif char in ('=', '!', '>', '<', '&', '|') \
            and not self.peek().isspace():
            pair_char = char + self.peek()
            if pair_char in tokens.COMP_OPS:
                return tokens.Token(pair_char,
                    tokens.COMP_OPS.get(pair_char), self.line)

        elif char in tokens.TTYPES:
            return tokens.Token(char, tokens.TTYPES.get(char), self.line)

        elif char == tokens.EOF:
            return tokens.Token(char, tokens.EOF, self.line)

    def tokenize(self, text):
        self.text = text
        self.reset()
        tokens = []
        while self.current_char != tokens.EOF:
            tokens.append(self.get_next_token())
        return tokens
