

from . import operators
from .enums import TokenType, Direction
from .token import Token


# A file or other module
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


# A currently running function
class Frame:
    __slots__ = ("func", "stack", "ptr", "direction", "register", "locals", "_running")

    def __init__(self, func, args):
        self.func = func
        self.register = ""
        self.stack = [*args]
        self.ptr = [0, 0]
        self.direction = Direction.RIGHT
        self.locals = {}
        self._running = False

    def eval_token(self, token):
        if token.type == TokenType.NUM:
            return int(token.value)
        elif token.type == TokenType.STRING:
            return str(token.value)
        elif str(token) in self.locals:
            return self.locals[str(token)]
        else:
            return self.func.module.eval_token(token)

    def set_token(self, token, value):
        if token.type != TokenType.VAR:
            print("Attempt to set a non-variable token")
            exit(1)
        self.locals[str(token.value)] = value

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
        if self._running:
            print("Frame run invoked more than once")
            exit(1)
        self._running = True

        string_mode = False

        while self.func.graph.is_within(self.ptr):
            char = self.func.graph[self.ptr]

            result = None
            if string_mode:
                if char == '"':
                    self.stack.append(Token(TokenType.STRING, self.register))
                    self.register = False
                    string_mode = False
                else:
                    self.register += char
            elif char in operators.FLOW_CONTROL:
                result = operators.invoke_operator(char, self)
            elif char in operators.ACTIONS or char in operators.REFLECTION:
                self._push()
                result = operators.invoke_operator(char, self)
            elif char == '"':
                string_mode = True
            elif char == ' ':
                self._push()
            else:
                self.register += char

            if result is not None:
                if isinstance(result, Token):
                    self.stack.append(result)
                elif isinstance(result, Direction):
                    self.direction = result

            self._shift_pointer()

        if len(self.stack):
            return self.stack.pop()
        return None


# An instance of a type
class Instance:
    pass
