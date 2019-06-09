
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

    def get_subgraph(self, top, left, bottom, right):
        graph = Graph(bottom - top - 1, right - left - 1)
        for i in range(top, bottom):
            line = ""
            for j in range(left, right):
                line += self[i, j]
            graph.append(line)
        return graph


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
        return f"{self.__class__.__name__}(name={self.name}, arguments={self.arguments}, graph={self.graph})"


class Function(Block):

    __slots__ = ()

    def __init__(self, name, code):
        super().__init__(name, code)

    def make_frame(self, *args):
        from .interpreter import Frame
        tokens = []
        for arg in args:
            tokens.append(make_token(arg))
        return Frame(self, tokens)

    def invoke(self, *args):
        from .interpreter import GlobalState
        print(f"Invoking {self.name}")
        frame = self.make_frame(*args)
        return GlobalState.run_frame(frame)


def _find_bar(graph):
    for i in range(graph.height):
        if graph[i, 0] == '-':
            for j in range(graph.width):
                if graph[i, j] != '-':
                    break
            else:
                return i
    return None


class Type(Block):  # TODO: Implement types

    __slots__ = ("methods", "constructor")

    def __init__(self, name, code):
        from .parse import parse_graph
        super().__init__(name, code)
        self.methods = []
        self.constructor = None

        height = _find_bar(self.graph)
        const = self.graph.get_subgraph(0, 0, height, self.graph.width)
        rest = self.graph.get_subgraph(height+1, 0, self.graph.height, self.graph.width)

        self.constructor = Function(f"{self.name}_constructor", const)
        self.constructor.arguments = self.arguments
        self.methods, _, _ = parse_graph(rest)

    def invoke(self, *args):
        from .interpreter import GlobalState, Instance
        frame = self.constructor.make_frame(*args)
        stack = GlobalState.run_stack_frame(frame)
        return Instance(self, stack)


class Extern(Block):  # TODO: Implement externs

    __slots__ = ()

