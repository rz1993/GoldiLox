from errors import RuntimeException

class Environment:
    def __init__(self, env=None):
        self.enclosing = env
        self.sym_table = dict()

    def get(self, var):
        if var.value in self.sym_table:
            return self.sym_table.get(var.value)

        if self.enclosing is not None:
            return self.enclosing.get(var)

        raise RuntimeException(
            var,
            "Variable \'{}\' is undefined".format(var.value)
        )

    def assign(self, var, val):
        if var.value in self.sym_table:
            self.sym_table[var.value] = val
            return

        if self.enclosing is not None:
            self.enclosing.assign(var, val)
            return

        raise RuntimeException(
            var,
            "Variable \'{}\' is undefined".format(var.value)
        )

    def define(self, var, initial_val=None):
        self.sym_table[var.value] = initial_val
