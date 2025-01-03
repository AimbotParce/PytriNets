import gravis as gv

from ..nets.petri import Marking
from ..nets.reachability import reachability


def display_reachability(initial_marking: Marking):
    """Plot the reachability graph of a Petri net its initial marking."""
    graph = reachability(initial_marking)
    nodes = list(graph.nodes)

    node_ids = {}
    node_data = []
    for j, node in enumerate(nodes):
        node_ids[node] = j
        node_data.append({"label": str(node), "metadata": {}})

    edge_data = []
    for source_node in graph.nodes:
        source = node_ids[source_node]
        for dest_node in source_node.outgoing_nodes:
            dest = node_ids[dest_node]
            edge_data.append({"source": source, "target": dest, "metadata": {}})

    plot_data = {
        "graph": {
            "directed": True,
            "metadata": {},
            "nodes": node_data,
            "edges": edge_data,
        }
    }

    gv.d3(plot_data, node_label_data_source="label").display()
