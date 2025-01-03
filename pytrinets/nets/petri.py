from abc import ABC
from collections import defaultdict
from typing import Generic, Self, TypeVar, Union


class Node(ABC):
    __name: str

    def __init__(self, name: str): ...

    @property
    def name(self) -> str: ...


class Place(Node):
    def __init__(self, name: str):
        self.__name = name

    @property
    def name(self) -> str:
        return self.__name

    def __str__(self) -> str:
        return self.__name

    def __repr__(self) -> str:
        return f"Place({self.__name})"


class Transition(Node):
    def __init__(self, name: str, incoming_places: set[Place] = None, outgoing_places: set[Place] = None):
        self.__name = name
        self.__incoming_places: set[Place] = incoming_places if incoming_places else set()
        self.__outgoing_places: set[Place] = outgoing_places if outgoing_places else set()

    @property
    def name(self) -> str:
        return self.__name

    def __str__(self) -> str:
        return self.__name

    def __repr__(self) -> str:
        return f"Transition({self.name}, {self.__incoming_places}, {self.__outgoing_places})"

    @property
    def incoming_places(self) -> set[Place]:
        return self.__incoming_places

    @property
    def outgoing_places(self) -> set[Place]:
        return self.__outgoing_places

    def add_incoming_place(self, place: Place):
        self.__incoming_places.add(place)

    def add_outgoing_place(self, place: Place):
        self.__outgoing_places.add(place)

    def remove_incoming_place(self, place: Place):
        self.__incoming_places.remove(place)

    def remove_outgoing_place(self, place: Place):
        self.__outgoing_places.remove(place)


class PetriNet:
    def __init__(self, places: set[Place] = None, transitions: set[Transition] = None):
        self.__places = places if places else set()
        self.__places_map = {place.name: place for place in self.__places}
        self.__transitions = transitions if transitions else set()
        self.__transitions_map = {transition.name: transition for transition in self.__transitions}

    @property
    def places(self) -> set[Place]:
        return self.__places

    @property
    def transitions(self) -> set[Transition]:
        return self.__transitions

    def __add_place(self, place: Place):
        if place.name in self.__places_map:
            raise ValueError(f"Place with name '{place.name}' already exists in this Petri net.")
        self.__places.add(place)
        self.__places_map[place.name] = place

    def __add_transition(self, transition: Transition):
        if transition.name in self.__transitions_map:
            raise ValueError(f"Transition with name '{transition.name}' already exists in this Petri net.")
        if not all(place in self.__places for place in transition.incoming_places) or not all(
            place in self.__places for place in transition.outgoing_places
        ):
            raise ValueError("All incoming and outgoing places of a transition must be in the Petri net.")
        self.__transitions.add(transition)
        self.__transitions_map[transition.name] = transition

    def add_place(self, name: str):
        self.__add_place(Place(name))

    def add_transition(self, name: str, incoming_places: set[str] = None, outgoing_places: set[str] = None):
        if incoming_places is None:
            incoming_places = set()
        if outgoing_places is None:
            outgoing_places = set()
        incoming_places = {place for place in self.__places if place.name in incoming_places}
        outgoing_places = {place for place in self.__places if place.name in outgoing_places}
        self.__add_transition(Transition(name, incoming_places, outgoing_places))

    def compile_marking(self, marking: dict[str, int]) -> dict[Place, int]:
        return {self.__places_map[name]: tokens for name, tokens in marking.items()}

    def as_marked(self, marking: dict[str, int] = None) -> "Marking":
        """Returns a marked version of this Petri net. The marked version is a copy of this Petri net where each place
        is marked with any amount of tokens tokens."""
        if marking is None:
            marking = {place: 0 for place in self.__places}
        else:
            marking = self.compile_marking(marking)
        return Marking(self, marking)

    def __repr__(self) -> str:
        return f"PetriNet({self.__places}, {self.__transitions})"

    def __str__(self) -> str:
        return f"Places: {", ".join(map(str, self.__places))}\nTransitions: {", ".join(map(str, self.__transitions))}"


class Marking:
    def __init__(self, origin: PetriNet, marking: dict[Place, int] = {}):
        self.__origin = origin
        self.__marking = defaultdict(int, marking)

    @property
    def origin(self) -> PetriNet:
        return self.__origin

    @property
    def places(self) -> set[Place]:
        return self.__origin.places

    @property
    def transitions(self) -> set[Transition]:
        return self.__origin.transitions

    def __getitem__(self, place: Place) -> int:
        return self.__marking[place]

    def _compute_available_transitions(self) -> set[tuple[Transition, Self]]:
        """Returns the set of all possible transitions that can be performed from the current marking, as well as the
        marking that results from firing each transition."""
        markings = set[tuple[Transition, Self]]()
        for transition in self.__origin.transitions:
            if self.can_fire(transition):
                markings.add((transition, self.fire(transition)))
        return markings

    def available_transitions(self) -> set[Transition]:
        """Returns the set of all possible transitions that can be performed from the current marking."""
        return {transition for transition, _ in self._compute_available_transitions()}

    def available_markings(self) -> set[Self]:
        """Returns the set of all possible markings that can be reached from the current marking by firing a single
        transition."""
        return {marking for _, marking in self._compute_available_transitions()}

    def can_fire(self, transition: Transition) -> bool:
        """Returns whether the given transition can be fired from the current marking."""
        return all(self.__marking[place] > 0 for place in transition.incoming_places)

    def fire(self, transition: Transition) -> Self:
        """Returns the marking that results from firing the given transition."""
        marking = self.__marking.copy()
        for place in transition.incoming_places:
            marking[place] -= 1
        for place in transition.outgoing_places:
            marking[place] += 1
        return Marking(self.__origin, marking)

    def __str__(self) -> str:
        return ", ".join(f"{place.name} ({tokens})" for place, tokens in self.__marking.items() if tokens > 0)

    def __repr__(self) -> str:
        return f"Marking({repr(self.__origin)}, {self.__marking})"

    def __hash__(self) -> int:
        return hash(self.__origin) + sum(hash(place) * tokens for place, tokens in self.__marking.items())

    def __eq__(self, other: Self) -> bool:
        if not self.__origin == other.origin:
            return False
        if not isinstance(other, Marking):
            return False
        for place in self.__origin.places:
            if self.__marking[place] != other.__marking[place]:
                return False
        return True
