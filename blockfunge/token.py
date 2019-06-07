
from .enums import TokenType


class Token:

    __slots__ = ("type", "value")

    def __init__(self, type, value):
        self.type = type
        self.value = value

    def __str__(self):
        return str(self.value)


def make_token(arg):
    if isinstance(arg, Token):
        return arg
    elif isinstance(arg, (int, float)):
        return Token(TokenType.NUM, arg)
    elif isinstance(arg, str):
        return Token(TokenType.STRING, arg)
    else:
        return Token(TokenType.REF, arg)
