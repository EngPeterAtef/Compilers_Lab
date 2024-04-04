from graph_visualize import GraphVisualize
from json_serialize import JsonSerialize
from parser_classes import *


class State:
    pass


@dataclass
class Edge:
    from_: State
    to_: State
    characters: set  # of chars (literals, epsilon) and pairs of chars (for ranges)


@dataclass
class DFA:
    start: State
    accept: list  # list of accepting states

    # All states of the NFA including the start and accept
    states: list  # of State
    transitions: list  # of Edge
