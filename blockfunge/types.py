
from .token import make_token


class Graph:

    def __init__(self, height=0, width=0):
        self.buffer = []
        self.height = height
        self.width = width

    def __len__(self):
        return len(self.buffer)

    def __repr__(self):
        return f"Graph(height={self.height}, width={self.width})"

    def __getitem__(self, item):
        if isinstance(item, (tuple, list)):
            if item[0] > self.height or item[1] > self.width:
                raise IndexError("Access outside graph size")
            try:
                return self.buffer[item[0]][item[1]]
            except IndexError:
                return None
        else:
            return self.buffer[item]

    def __setitem__(self, key, value):
        if isinstance(key, (tuple, list)):
            if key[0] > self.height or key[1] > self.width:
                raise IndexError("Access outside graph size")
            try:
                self.buffer[key[0]][key[1]] = value
            except IndexError:
                print("TODO: Key outside range")
        else:
            self.buffer[key] = value

    def is_within(self, point):
        return 0 <= point[0] < self.height and 0 <= point[1] < self.width

    def append(self, line):
        if len(line) > self.width:
            self.width = len(line)
        if len(self.buffer) + 1 > self.height:
            self.height += 1
        self.buffer.append(line)


class Block:

    __slots__ = ("name", "graph", "arguments", "module")

    def __init__(self, name, graph):
        arg_pos = name.find('[')
        self.arguments = 0
        if arg_pos > 0:
            self.arguments = int(name[arg_pos+1:len(name)-1])
            name = name[:arg_pos]
        self.name = name
        self.graph = graph

    def __repr__(self):
        return f"Block(name={self.name}, arguments={self.arguments}, graph={self.graph})"


class Function(Block):

    __slots__ = ()

    def __init__(self, name, code):
        super().__init__(name, code)

    def invoke(self, *args):
        from .interpreter import Frame
        tokens = []
        for arg in args:
            tokens.append(make_token(arg))
        print(f"Invoking {self.name}")
        frame = Frame(self, tokens)
        return self.module.add_frame(frame)


class Type(Block):  # TODO: Implement types

    __slots__ = ("methods",)


class Extern(Block):  # TODO: Implement externs
    pass

