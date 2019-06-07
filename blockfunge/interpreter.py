

from . import operators
from .enums import TokenType, Direction
from .types import Token


def make_token(arg):
    if isinstance(arg, Token):
        return arg
    elif isinstance(arg, (int, float)):
        return Token(TokenType.NUM, arg)
    elif isinstance(arg, str):
        return Token(TokenType.STRING, arg)
    else:
        return Token(TokenType.REF, arg)


class Module:

    def __init__(self, funcs, types, externs):
        self.funcs = funcs
        self.types = types
        self.externs = externs
        for func in funcs:
            funcs[func].module = self
        for type in types:
            types[type].module = self
        for extern in externs:
            externs[extern].module = self

        self.frames = []

    def eval_token(self, token):
        if str(token) in self.funcs:
            return self.funcs[str(token)]
        elif str(token) in self.types:
            return self.types[str(token)]
        print("Unknown Token")
        exit(1)

    def run(self):
        print(self.funcs["main"].invoke())

    def add_frame(self, frame):
        self.frames.append(frame)
        result = frame.run()
        self.frames.pop()
        return result


class Frame:
    __slots__ = ("func", "stack", "ptr", "direction", "register", "locals")

    def __init__(self, func, args):
        self.func = func
        self.register = ""
        self.stack = [*args]
        self.ptr = [0, 0]
        self.direction = Direction.RIGHT
        self.locals = {}

    def eval_token(self, token):
        if token.type == TokenType.NUM:
            return int(token.value)
        elif str(token) in self.locals:
            return self.locals[str(token)]
        else:
            return self.func.module.eval_token(token)

    def _shift_pointer(self):
        if self.direction == Direction.RIGHT:
            self.ptr[1] += 1
        elif self.direction == Direction.LEFT:
            self.ptr[1] -= 1
        elif self.direction == Direction.DOWN:
            self.ptr[0] += 1
        elif self.direction == Direction.UP:
            self.ptr[0] -= 1

    def _push(self):
        if self.register == "":
            return
        if self.register.isnumeric():
            ttype = TokenType.NUM
        else:
            ttype = TokenType.VAR
        self.stack.append(Token(ttype, self.register))
        self.register = ""

    def run(self):

        while self.func.graph.is_within(self.ptr):
            char = self.func.graph[self.ptr]

            if char in operators.FLOW_CONTROL:
                if self.register != "":
                    self._push()
                self.direction = operators.invoke_operator(char, self)
            elif char in operators.ACTIONS:
                self._push()
                result = operators.invoke_operator(char, self)
                if result is not None:
                    self.stack.append(make_token(result))
            elif char == '"':
                pass
                # TODO: String mode
            elif char == ' ':
                self._push()
            else:
                self.register += char

            self._shift_pointer()

        if len(self.stack):
            return self.stack.pop()
        return None
