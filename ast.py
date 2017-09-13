class AST:
    """ Abstract Syntax Tree with visitor pattern """
    def visit(self, interpreter):
        visit_func = "visit{}".format(self.__class__.__name__)
        func = getattr(interpreter, visit_func)
        return func(self)

class Grouping(AST):
    def __init__(self, expr):
        self.expr = expr

class Assignment(AST):
    def __init__(self, variable, expr):
        self.var = variable
        self.expr = expr

class Logical(AST):
    def __init__(self, left_expr, op_token, right_expr):
        self.left = left_expr
        self.op = op_token
        self.right = right_expr

class Binary(AST):
    def __init__(self, left_expr, op_token, right_expr):
        self.left = left_expr
        self.op = op_token
        self.right = right_expr

class Unary(AST):
    def __init__(self, op_token, operand_expr):
        self.op = op_token
        self.operand = operand_expr

class Literal(AST):
    def __init__(self, token):
        self.value = token.value

class Variable(AST):
    def __init__(self, token):
        self.var = token

class Call(AST):
    def __init__(self, callee, args):
        self.callee = callee
        self.args = args

class ExprStmt(AST):
    def __init__(self, expr):
        self.expr = expr

class PrintStmt(AST):
    def __init__(self, expr):
        self.expr = expr

class BlockStmt(AST):
    def __init__(self, stmts):
        self.stmts = stmts

class IfStmt(AST):
    def __init__(self, if_cond, if_branch, else_branch=None):
        self.if_cond = if_cond
        self.if_branch = if_branch
        self.else_branch = else_branch

class WhileStmt(AST):
    def __init__(self, cond, body):
        self.cond = cond
        self.body = body

class ReturnStmt(AST):
    def __init__(self, expr):
        self.expr = expr

class VarDecl(AST):
    def __init__(self, var, expr=None):
        self.var = var
        self.expr = expr

class FunDecl(AST):
    def __init__(self, name, params, body):
        self.name = name
        self.params = params
        self.body = body
