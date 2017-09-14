import ast
from tokens import Types


class ParseError(Exception):
    def __init__(self, token, msg):
        super(ParseError, self).__init__(msg)
        self.token = token
        self.line = token.line
        self.msg = msg


class Parser:
    def __init__(self, lox):
        self.lox = lox
        self.pos = 0
        self.statements = []

    def advance(self):
        if not self.is_at_end():
            token = self.tokens[self.pos]
            self.pos += 1
            return token

    def peek(self):
        return self.tokens[self.pos + 1]

    def current(self):
        if self.is_at_end():
            return self.tokens[-1]
        return self.tokens[self.pos]

    def previous(self):
        return self.tokens[self.pos - 1]

    def is_at_end(self):
        return self.tokens[self.pos].type == Types.EOF

    def check(self, *token_types):
        # Matching without advancing for looping
        return self.current().type in token_types

    def match(self, *token_types):
        if self.current().type in token_types:
            self.advance()
            return True
        return False

    def consume(self, token_type, msg):
        if self.match(token_type):
            return True
        raise self.error(self.current(), msg)

    def is_valid_lvalue(self, lvalue):
        # Check if ast node is a valid assignment target i.e. l-value
        return lvalue.__class__.__name__ == ast.Variable.__name__

    def error(self, token, msg):
        return ParseError(token, msg)

    def multi_pattern(self, prec_rule, ast_type, *valid_token_types):
        """ Helper method for building 0 or more left deep  """
        prec_func = getattr(self, prec_rule)
        left = prec_func()
        while self.match(*valid_token_types):
            op = self.previous()
            left = ast_type(left, op,
                prec_func())

        return left

    def expression(self):
        return self.assignment()

    def assignment(self):
        # let the var evaluate to an assignable value
        var = self.logic_or()

        if self.match(Types.EQUAL):
            # for error purposes
            equals = self.previous()
            # right hand could be another assignment expr
            expr = self.expression()
            if self.is_valid_lvalue(var):
                var_token = var.var
                return ast.Assignment(var_token, expr)

            raise self.error(equals, "Invalid assignment target")

        return var

    def logic_or(self):
        return self.multi_pattern(
            "logic_and",
            ast.Logical,
            Types.LOGIC_OR)

    def logic_and(self):
        return self.multi_pattern(
            "equality",
            ast.Logical,
            Types.LOGIC_AND
        )

    def equality(self):
        return self.multi_pattern(
            "comparison",
            ast.Binary,
            Types.EQUAL_EQUAL,
            Types.BANG_EQUAL
        )

    def comparison(self):
        return self.multi_pattern(
            "addition",
            ast.Binary,
            Types.LTE,
            Types.GTE,
            Types.LT,
            Types.GT
        )

    def addition(self):
        return self.multi_pattern(
            "multiplication",
            ast.Binary,
            Types.PLUS,
            Types.MINUS
        )

    def multiplication(self):
        return self.multi_pattern(
            "unary",
            ast.Binary,
            Types.STAR,
            Types.SLASH
        )

    def unary(self):
        if self.match(Types.MINUS, Types.BANG):
            op = self.previous()
            operand = self.unary()
            return ast.Unary(op, operand)
        return self.call()

    def call(self):
        callee = self.primary()
        while self.match(Types.LPAREN):
            args = self.arguments()
            callee = ast.Call(callee, args)
            self.consume(Types.RPAREN, "Expected \')\' after function call")
        return callee

    def arguments(self):
        # Parsing function arguments
        args = []
        if not self.check(Types.RPAREN):
            args.append(self.expression())
            while self.match(Types.COMMA):
                args.append(self.expression())

        return args

    def primary(self):
        if self.match(Types.LPAREN):
            expr = self.expression()
            self.consume(Types.RPAREN, "Expected closing parenthesis )")
            return ast.Grouping(expr)
        if self.match(Types.NUMBER, Types.STRING, Types.NIL):
            return ast.Literal(self.previous())
        if self.match(Types.IDENTIFIER):
            return ast.Variable(self.previous())

        raise self.error(self.current(), "Expected expression")

    def statement(self):
        if self.match(Types.PRINT):
            return self.print_stmt()
        if self.match(Types.LBRACE):
            return self.block()
        if self.match(Types.IF):
            return self.if_stmt()
        if self.match(Types.WHILE):
            return self.while_stmt()
        if self.match(Types.FOR):
            return self.for_stmt()
        if self.match(Types.RETURN):
            return self.return_stmt()

        return self.expr_stmt()

    def expr_stmt(self):
        expr = self.expression()
        self.consume(Types.SEMICOLON, "Expected semicolon")
        return ast.ExprStmt(expr)

    def print_stmt(self):
        expr = self.expression()
        self.consume(Types.SEMICOLON, "Expected semicolon")
        return ast.PrintStmt(expr)

    def if_stmt(self):
        if_cond = self.expression()
        if_branch = self.statement()

        if self.match(Types.ELSE):
            return ast.IfStmt(if_cond, if_branch, self.statement())

        return ast.IfStmt(if_cond, if_branch)

    def while_stmt(self):
        self.consume(
            Types.LPAREN,
            'Expected opening parenthesis after \'while\''
            )
        cond = self.expression()
        self.consume(
            Types.RPAREN,
            'Expected closing parenthesis'
        )
        body = self.declaration()
        return ast.WhileStmt(cond, body)

    def for_stmt(self):
        # Syntactic sugar using while statement and an initializer
        self.consume(Types.LPAREN, 'Expected \'(\' after \'for\'')
        # Get the optional initializer expression
        if self.match(Types.SEMICOLON):
            initializer = None
        elif self.match(Types.VAR):
            initializer = self.var_declaration()
        elif self.match(Types.IDENTIFIER):
            initializer = self.expr_stmt()
        else:
            raise self.error(
                self.current(),
                "Invalid initial expression after \'for\'"
            )
        # Get the optional loop condition
        if not self.check(Types.SEMICOLON):
            cond = self.expression()
        else:
            # Omitted condition is equivalent to always True
            cond = ast.Literal(Token("True", Types.TRUE, self.current().line, True))
        self.consume(Types.SEMICOLON, "Expected \';\' after loop condition")

        # Get the incrementing expression
        increment = self.expression() if not self.check(Types.RPAREN) else None
        self.consume(Types.RPAREN, "Expected \')\' after for loop clauses")

        body = self.statement()

        if increment is not None:
            body = ast.BlockStmt([increment, body])

        loop = ast.WhileStmt(cond, body)
        if initializer is not None:
            loop = ast.BlockStmt([initializer, loop])

        return loop

    def return_stmt(self):
        expr = self.expression()
        self.consume(Types.SEMICOLON, "Expected \';\' after return statement")
        return ast.ReturnStmt(expr)

    def block(self):
        # A block of statements enclosed by braces that enables
        # its own scope
        block = []
        while not self.check(Types.RBRACE) and \
            not self.is_at_end():
             block.append(self.declaration())
        self.consume(Types.RBRACE, "Expected closing brace")
        return ast.BlockStmt(block)

    def declaration(self):
        # Includes variable, function and class definition or stmts
        if self.match(Types.VAR):
            return self.var_declaration()
        if self.match(Types.FUN):
            return self.fun_declaration("function")
        return self.statement()

    def var_declaration(self):
        self.consume(Types.IDENTIFIER, "Expected variable name")
        variable = self.previous()
        initializer = None
        if self.match(Types.EQUAL):
            initializer = self.expression()
            self.consume(Types.SEMICOLON, "Expected semicolon")
            return ast.VarDecl(variable, initializer)
        return ast.VarDecl(variable)

    def fun_declaration(self, kind):
        # Kind parameter used to distinguish errors
        # for method and function declarations
        self.consume(Types.IDENTIFIER, "Expected {} name".format(kind))
        name = self.previous()
        self.consume(Types.LPAREN, "Expected \'(\' after {} name".format(kind))
        params = self.arguments()
        self.consume(Types.RPAREN, "Expected \')\' after parameter definition")
        body = self.statement()
        return ast.FunDecl(name, params, body)

    def parse(self, tokens):
        self.tokens = tokens
        self.pos = 0
        self.statements = []
        try:
            while not self.is_at_end():
                self.statements.append(self.declaration())
        except ParseError as error:
            self.lox.parsing_error(error)
        return self.statements
