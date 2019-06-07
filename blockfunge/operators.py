
from .enums import Direction, TokenType
from .token import Token, make_token
import inspect


def pop_token(frame):
    return frame.stack.pop()


def pop_value(frame):
    return frame.eval_token(frame.stack.pop())


def up_arrow():
    return Direction.UP


def down_arrow():
    return Direction.DOWN


def left_arrow():
    return Direction.LEFT


def right_arrow():
    return Direction.RIGHT


def open_gate(frame):
    result = pop_value(frame)
    if result is True:
        return frame.direction
    else:
        return frame.direction.reverse()


def close_gate(frame):
    result = pop_value(frame)
    if result is True:
        return frame.direction.reverse()
    else:
        return frame.direction


def reverse(frame):
    return frame.direction.reverse()


def skip(frame):
    frame._shift_pointer()
    return frame.direction


def skip_cond(frame):
    a = pop_value(frame)
    if a:
        frame._shift_pointer()
    return frame.direction


FLOW_CONTROL = {
    '^': up_arrow,
    'v': down_arrow,
    '<': left_arrow,
    '>': right_arrow,
    '[': open_gate,
    ']': close_gate,
    ':': reverse,
    ';': skip,
    '?': skip_cond
}


def add(frame):
    a = pop_value(frame)
    b = pop_value(frame)
    return a + b


def subtract(frame):
    a = pop_value(frame)
    b = pop_value(frame)
    return a - b


def multiply(frame):
    a = pop_value(frame)
    b = pop_value(frame)
    return a * b


def divide(frame):
    a = pop_value(frame)
    b = pop_value(frame)
    return a / b


def modulo(frame):
    a = pop_value(frame)
    b = pop_value(frame)
    return a % b


def bool_not(frame):
    a = pop_value(frame)
    return not a


def bool_and(frame):
    a = pop_value(frame)
    b = pop_value(frame)
    return a and b


def bool_or(frame):
    a = pop_value(frame)
    b = pop_value(frame)
    return a or b


def bool_xor(frame):
    a = pop_value(frame)
    b = pop_value(frame)
    return a ^ b


def compare(frame):
    a = pop_value(frame)
    b = pop_value(frame)
    return a == b


def set_var(frame):
    tok = pop_token(frame)
    val = pop_value(frame)
    frame.set_token(tok, val)


def sub_obj(frame):
    from .interpreter import Module, Instance
    val = pop_value(frame)
    tok = pop_token(frame)
    if not isinstance(val, (Module, Instance)):
        print("Cannot get sub-object of literal value")
    return tok.eval_token(tok)


def call(frame):
    func = pop_value(frame)
    num_args = func.arguments
    args = []
    for arg in range(num_args):
        args.append(pop_value(frame))
    return func.invoke(*args)


ACTIONS = {
    '+': add,
    '-': subtract,
    '*': multiply,
    '/': divide,
    '%': modulo,
    '!': bool_not,
    '&': bool_and,
    '|': bool_or,
    '~': bool_xor,
    '#': compare,
    '=': set_var,
    '.': sub_obj,
    '(': call
}


def stacksize(frame):
    return len(frame.stack)


def stringize(frame):
    token = pop_token(frame)
    return str(token)


def tokenize(frame):
    val = pop_value(frame)
    return Token(TokenType.VAR, str(val))


def pop(frame):
    frame.stack.pop()


def get_char(frame):
    a = pop_value(frame)
    b = pop_value(frame)
    return frame.func.graph[a, b]


def set_char(frame):
    a = pop_value(frame)
    b = pop_value(frame)
    c = pop_value(frame)
    frame.func.graph[a, b] = c


REFLECTION = {
    '`': stacksize,
    '\'': stringize,
    '\\': tokenize,
    ',': pop,
    '@': get_char,
    '$': set_char
}


ALL_OPS = FLOW_CONTROL.copy()
ALL_OPS.update(ACTIONS)
ALL_OPS.update(REFLECTION)


def invoke_operator(op, frame):
    func = ALL_OPS[op]
    sig = inspect.signature(func)
    if len(sig.parameters) > 0:
        out = func(frame)
    else:
        out = func()
    if out is not None and not isinstance(out, Direction):
        return make_token(out)
    return out
