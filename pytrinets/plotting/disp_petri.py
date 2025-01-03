from typing import Union

import gravis as gv
import numpy as np
from PIL import Image, ImageDraw, ImageShow

from ..nets.petri import Marking, PetriNet


def __get_petri_graph_data(petrinet: PetriNet):
    places = list(petrinet.places)
    transitions = list(petrinet.transitions)

    place_ids = {}
    node_data = []
    for place in places:
        place_ids[place] = len(node_data)
        node_data.append(
            {
                "label": str(place),
                "metadata": {
                    "shape": "circle",
                    "border_color": "black",
                    "color": "white",
                    "border_size": 2,
                    "size": 20,
                },
            }
        )

    edge_data = []
    for transition in transitions:
        transition_id = len(node_data)
        node_data.append(
            {
                "label": str(transition),
                "metadata": {
                    "shape": "rectangle",
                    "border_color": "black",
                    "color": "white",
                    "border_size": 2,
                    "size": 20,
                },
            }
        )
        for source_place in transition.incoming_places:
            source = place_ids[source_place]
            edge_data.append({"source": source, "target": transition_id, "metadata": {}})
        for dest_place in transition.outgoing_places:
            dest = place_ids[dest_place]
            edge_data.append({"source": transition_id, "target": dest, "metadata": {}})

    plot_data = {
        "graph": {
            "directed": True,
            "metadata": {},
            "nodes": node_data,
            "edges": edge_data,
        }
    }
    return plot_data


def __generate_token_image(token_count: int):
    size = 80
    arr = np.full((size, size, 4), 255, dtype=np.uint8)
    arr[:, :, 3] = 0
    image = Image.fromarray(arr)

    draw = ImageDraw.Draw(image)
    dots_per_row = np.ceil(np.sqrt(token_count)).astype(int)
    total_rows = np.ceil(token_count / dots_per_row).astype(int)
    dot_size = size // dots_per_row - 4

    for i in range(token_count):
        row = i // dots_per_row
        col = i % dots_per_row
        x = col * (dot_size + 2) + 1
        y = row * (dot_size + 2) + 1 + (size - total_rows * (dot_size + 2)) // 2
        draw.ellipse([x, y, x + dot_size, y + dot_size], fill="black")

    return image


def __get_marking_graph_data(marking: Marking):
    places = list(marking.places)
    transitions = list(marking.transitions)

    place_ids = {}
    node_data = []
    for place in places:
        place_ids[place] = len(node_data)

        data = {
            "label": str(place),
            "metadata": {
                "shape": "circle",
                "border_color": "black",
                "color": "white",
                "border_size": 2,
                "size": 20,
            },
        }
        if marking[place] > 0:
            image = __generate_token_image(marking[place])
            image_path = ImageShow._viewers[0].save_image(image)
            data["metadata"]["image"] = gv.convert.image_to_data_url(image_path)
        node_data.append(data)

    edge_data = []
    for transition in transitions:
        transition_id = len(node_data)
        node_data.append(
            {
                "label": str(transition),
                "metadata": {
                    "shape": "rectangle",
                    "border_color": "black",
                    "color": "white",
                    "border_size": 2,
                    "size": 20,
                },
            }
        )
        for source_place in transition.incoming_places:
            source = place_ids[source_place]
            edge_data.append({"source": source, "target": transition_id, "metadata": {}})
        for dest_place in transition.outgoing_places:
            dest = place_ids[dest_place]
            edge_data.append({"source": transition_id, "target": dest, "metadata": {}})

    plot_data = {
        "graph": {
            "directed": True,
            "metadata": {},
            "nodes": node_data,
            "edges": edge_data,
        }
    }
    return plot_data


def display_petri(petrinet: Union[PetriNet, Marking]):
    """Plot the reachability graph of a Petri net its initial marking."""

    if isinstance(petrinet, PetriNet):
        plot_data = __get_petri_graph_data(petrinet)
    elif isinstance(petrinet, Marking):
        plot_data = __get_marking_graph_data(petrinet)

    gv.d3(plot_data, node_label_data_source="label").display()
