from collections import deque
from typing import Union

from .petri import Marking, PetriNet


class ReachabilityNode:
    def __init__(
        self,
        marking: Marking,
        incoming_nodes: set["ReachabilityNode"] = None,
        outgoing_nodes: set["ReachabilityNode"] = None,
    ):
        self.__marking = marking
        self.__incoming_nodes: set[ReachabilityNode] = incoming_nodes if incoming_nodes else set()
        self.__outgoing_nodes: set[ReachabilityNode] = outgoing_nodes if outgoing_nodes else set()

    @property
    def marking(self) -> Marking:
        return self.__marking

    def __eq__(self, other: "ReachabilityNode") -> bool:
        return self.__marking == other.__marking if isinstance(other, ReachabilityNode) else False

    def __str__(self) -> str:
        return "{" + str(self.__marking) + "}"

    def __repr__(self) -> str:
        return f"ReachabilityNode({self.__marking}, {self.__incoming_nodes}, {self.__outgoing_nodes})"

    def __hash__(self) -> int:
        return hash(self.__marking)

    @property
    def incoming_nodes(self) -> set["ReachabilityNode"]:
        return self.__incoming_nodes

    @property
    def outgoing_nodes(self) -> set["ReachabilityNode"]:
        return self.__outgoing_nodes

    def add_incoming_node(self, node: "ReachabilityNode"):
        self.__incoming_nodes.add(node)

    def add_outgoing_node(self, node: "ReachabilityNode"):
        self.__outgoing_nodes.add(node)

    def remove_incoming_node(self, node: "ReachabilityNode"):
        self.__incoming_nodes.remove(node)

    def remove_outgoing_node(self, node: "ReachabilityNode"):
        self.__outgoing_nodes.remove(node)


class ReachabilityGraph:
    def __init__(self, initial_node: ReachabilityNode, nodes: set[ReachabilityNode]):
        self.__initial_node = initial_node
        self.__nodes: set[ReachabilityNode] = nodes

    @property
    def petrinet(self) -> PetriNet:
        return self.__initial_node.marking.origin

    @property
    def initial_marking(self) -> Marking:
        return self.__initial_node.marking

    @property
    def nodes(self) -> set[ReachabilityNode]:
        return self.__nodes


def reachability(initial_marking: Marking) -> ReachabilityGraph:
    """Computes the reachability graph of a Petri net given an initial marking."""
    root = ReachabilityNode(initial_marking)
    visited = dict[Marking, ReachabilityNode]()
    queue = deque[ReachabilityNode]([root])
    dead_ends = set[ReachabilityNode]()  # For now, we will not use this set

    while queue:
        current = queue.popleft()
        if current.marking in visited:
            continue
        visited[current.marking] = current
        available_markings = initial_marking.available_markings()
        if not available_markings:
            dead_ends.add(current)
            continue
        for initial_marking in available_markings:
            if initial_marking in visited:
                new_node = visited[initial_marking]
            else:
                new_node = ReachabilityNode(initial_marking)
                queue.append(new_node)
            current.add_outgoing_node(new_node)
            new_node.add_incoming_node(current)

    return ReachabilityGraph(root, set(visited.values()))