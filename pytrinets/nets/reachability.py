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
    def __init__(
        self, initial_node: ReachabilityNode, nodes: set[ReachabilityNode], dead_ends: set[ReachabilityNode] = None
    ):
        self.__initial_node = initial_node
        self.__nodes: set[ReachabilityNode] = nodes
        self.__dead_ends: set[ReachabilityNode] = dead_ends if dead_ends else set()

    @property
    def petrinet(self) -> PetriNet:
        return self.__initial_node.marking.origin

    @property
    def initial_marking(self) -> Marking:
        return self.__initial_node.marking

    @property
    def nodes(self) -> set[ReachabilityNode]:
        return self.__nodes

    @property
    def dead_ends(self) -> set[ReachabilityNode]:
        return self.__dead_ends


def reachability(
    initial_marking: Marking, max_iterations: int = 100_000, throw_error: bool = True
) -> ReachabilityGraph:
    """Computes the reachability graph of a Petri net given an initial marking.

    Max iterations is the maximum number of iterations the algorithm will run before stopping.
    It is there to prevent infinite loops in the case of an unbounded Petri net.

    If throw_error is True, the function will raise an error if the maximum number of iterations is reached.
    """
    root = ReachabilityNode(initial_marking)
    visited = dict[Marking, ReachabilityNode]()
    queue = deque[ReachabilityNode]([root])
    dead_ends = set[ReachabilityNode]()  # For now, we will not use this set

    it = 0
    while queue:
        current = queue.popleft()
        if current.marking in visited:
            continue
        visited[current.marking] = current
        available_markings = current.marking.available_markings()
        if not available_markings:
            dead_ends.add(current)
            continue
        for marking in available_markings:
            if marking in visited:
                new_node = visited[marking]
            else:
                new_node = ReachabilityNode(marking)
                queue.append(new_node)
            current.add_outgoing_node(new_node)
            new_node.add_incoming_node(current)
        it += 1
        if it >= max_iterations:
            if throw_error:
                raise ValueError("Maximum number of iterations reached.")
            break

    return ReachabilityGraph(root, set(visited.values()), dead_ends)
