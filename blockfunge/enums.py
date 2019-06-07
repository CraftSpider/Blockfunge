
import enum


class Direction(enum.Enum):
    UP = 0
    RIGHT = 1
    DOWN = 2
    LEFT = 3

    def reverse(self):
        return Direction((self.value + 2) % 4)


class BlockType(enum.Enum):
    FUNCTION = enum.auto()
    CLASS = enum.auto()
    EXTERN = enum.auto()


class TokenType:
    STRING = enum.auto()
    NUM = enum.auto()
    VAR = enum.auto()
    REF = enum.auto()
