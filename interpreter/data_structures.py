from environment import Environment
from errors import ReturnException

class LoxCallable:
    def arity(self):
        pass

    def call(self, interpreter, args):
        pass

class LoxFunction(LoxCallable):
    def __init__(self, declaration, closure):
        self.params = declaration.params
        self.body = declaration.body
        self.closure = closure

    def call(self, interpreter, args):
        # Create a new environment for the function object
        # whose parent is the environment in which it was defined
        environment = Environment(self.closure)
        for i in range(len(self.params)):
            environment.define(self.params[i].var, args[i])
        # Pass this function's environment to the interpreter
        # Which will set and exit the function's environment after the call
        return interpreter.execute_block(self.body, environment)
