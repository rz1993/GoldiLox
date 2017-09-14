class ReturnException(Exception):
    def __init__(self, val):
        self.value = val

class RuntimeException(Exception):
    def __init__(self, token, msg=None):
        if msg is None:
            msg = "Runtime Exception on line {}".format(token.line)
        super(RuntimeException, self).__init__(msg)
        self.token = token
        self.line = token.line
