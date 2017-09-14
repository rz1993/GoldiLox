from tokens import Types
from data_structures import LoxCallable, LoxFunction
from environment import Environment
from errors import ReturnException, RuntimeException


MAX_PARAMS = 16


class Interpreter:
    def __init__(self, lox):
        self.lox = lox
        self.globals = Environment()
        self.current_env = self.globals

    def evaluate(self, ast):
        return ast.visit(self)

    def execute(self, stmt):
        return stmt.visit(self)

    def execute_block(self, stmt, environment):
        prev_env = self.current_env
        self.current_env = environment
        print(environment.sym_table)
        # Use ReturnException to unwind the statement call stacks
        # when a return statement is evaluated. Note that the exception
        # handling should be done here so that the environment is always
        # reset after a function exits; if exception handling is done at
        # a higher level, i.e. at the LoxFunction.call() level, then
        # exceptions raised will cause execute_block() to never reset
        # the environment to what it was previously
        try:
            return_val = self.execute(stmt)
        except ReturnException as return_object:
            return_val = return_object.value
        self.current_env = prev_env
        return return_val

    def check_numeric(self, val):
        return type(val) == int or type(val) == float

    def check_string(self, val):
        return type(val) == str

    def check_numeric_operands(self, op, *operands):
        for o in operands:
            if not self.check_numeric(o):
                raise RuntimeException(op,
                    "{} operator expected numeric operands".format(op.value))
        return True

    def is_truthy(self, val):
        if val is None:
            return False
        if type(val) == bool:
            return val
        return True

    def is_equal(self, a, b):
        if a is None and b is None:
            return True
        if a is None:
            return False
        return a == b

    def is_callable(self, call_val):
        return isinstance(call_val, LoxCallable)

    def interpret(self, stmts):
        try:
            for ast in stmts:
                self.execute(ast)
        except RuntimeException as error:
            """ Catch runtime exception and leave the
            implementation up to the Lox program. """
            self.lox.runtime_error(error)

    def visitLiteral(self, ast):
        return ast.value

    def visitGrouping(self, ast):
        return self.evaluate(ast.expr)

    def visitAssignment(self, ast):
        val = self.evaluate(ast.expr)
        self.current_env.assign(ast.var, val)

    def visitLogical(self, ast):
        # Code for logical and binary expressions differ
        left_val = self.evaluate(ast.left)
        if ast.op.type == Types.LOGIC_OR:
            # If left value is true then short circuit OR and return it
            if self.is_truthy(left_val):
                return left_val
        else:
            # If AND and left value is False, short circuit and return it
            if not self.is_truthy(left_val):
                return left_val

        # Otherwise OR returns right value if left is False
        # And OR returns right value when both are True
        return self.evaluate(ast.right)

    def visitBinary(self, ast):
        """ For binary expressions """
        left = self.evaluate(ast.left)
        right = self.evaluate(ast.right)

        if ast.op.type == Types.STAR:
            self.check_numeric_operands(ast.op, left, right)
            return left * right

        if ast.op.type == Types.SLASH:
            self.check_numeric_operands(ast.op, left, right)
            return left / right

        if ast.op.type == Types.MINUS:
            self.check_numeric_operands(ast.op, left, right)
            return left - right

        if ast.op.type == Types.PLUS:
            if self.check_numeric(left) and self.check_numeric(right):
                return left + right

            if self.check_string(left) and self.check_string(right):
                return left + right

            raise RuntimeException(ast.op,
                "Unsupported operand type(s) {} and {} for {}".format(
                    type(left), type(right), ast.op.text
                ))

        if ast.op.type == Types.BANG_EQUAL:
            return not self.is_equal(left, right)

        if ast.op.type == Types.EQUAL_EQUAL:
            return self.is_equal(left, right)

        if ast.op.type == Types.GTE:
            self.check_numeric_operands(ast.op, left, right)
            return left >= right

        if ast.op.type == Types.GT:
            self.check_numeric_operands(ast.op, left, right)
            return left > right

        if ast.op.type == Types.LTE:
            self.check_numeric_operands(ast.op, left, right)
            return left <= right

        if ast.op.type == Types.LT:
            self.check_numeric_operands(ast.op, left, right)
            return left < right

    def visitUnary(self, ast):
        if ast.op.type == Types.BANG:
            val = self.evaluate(ast.operand)
            return not self.is_truthy(val)

        if ast.op.type == Types.MINUS:
            val = self.evaluate(ast.operand)
            if self.check_numeric_operands(ast.op, val):
                return -val

    def visitCall(self, ast):
        callee = self.evaluate(ast.callee)
        if not self.is_callable(callee):
            raise Exception("Not a callable")

        args = [self.evaluate(arg) for arg in ast.args]
        return callee.call(self, args)

    def visitVariable(self, ast):
        return self.current_env.get(ast.var)

    def visitExprStmt(self, ast):
        value = self.evaluate(ast.expr)
        return value

    def visitPrintStmt(self, ast):
        value = self.evaluate(ast.expr)
        print(value)

    def visitIfStmt(self, ast):
        if self.is_truthy(self.evaluate(ast.if_cond)):
            return self.execute(ast.if_branch)
        elif ast.else_branch is not None:
            return self.execute(ast.else_branch)

    def visitWhileStmt(self, ast):
        while self.is_truthy(self.evaluate(ast.cond)):
            self.execute(ast.body)

    def visitBlockStmt(self, ast):
        # Initialize a new scope tied to the block
        self.current_env = Environment(self.current_env)

        for stmt in ast.stmts:
            self.execute(stmt)

        self.current_env = self.current_env.enclosing

    def visitReturnStmt(self, ast):
        # Raise an exception through the statement call stack
        return_value = self.evaluate(ast.expr)
        raise ReturnException(return_value)

    def visitVarDecl(self, ast):
        if ast.expr is not None:
            self.current_env.define(ast.var, self.evaluate(ast.expr))
            return
        self.current_env.define(ast.var)

    def visitFunDecl(self, func_decl):
        # Create a LoxFunction object that will be stored
        # Pass the declaration to set its parameters and executable body
        # Pass the current environment to the LoxFunction to enable closure
        if len(func_decl.params) > MAX_PARAMS:
            last_token = func_decl.params[-1]
            raise RuntimeException(last_token,
                "Maximum number of parameters exceeded")
        func = LoxFunction(func_decl, self.current_env)
        self.current_env.define(func_decl.name, func)
