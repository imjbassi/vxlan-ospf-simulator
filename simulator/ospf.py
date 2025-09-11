from __future__ import annotations
from typing import TYPE_CHECKING, Dict, Tuple
import networkx as nx

if TYPE_CHECKING:
    from .topology import Fabric

def compute_spf_for_node(graph: nx.Graph, start_node: str) -> Dict[str, Tuple[str, int]]:
    """
    Computes Shortest Path First (Dijkstra's) for a single node.
    Returns a routing table: {destination: (next_hop, cost)}
    """
    paths = nx.single_source_dijkstra_path(graph, start_node, weight="cost")
    costs = nx.single_source_dijkstra_path_length(graph, start_node, weight="cost")
    
    routing_table = {}
    for dest, path in paths.items():
        if start_node == dest:
            continue
        next_hop = path[1] if len(path) > 1 else dest
        routing_table[dest] = (next_hop, costs[dest])
        
    return routing_table

def install_routes_for_all(graph: nx.Graph) -> Dict[str, Dict[str, Tuple[str, int]]]:
    """
    Computes SPF for all nodes in the graph and returns all routing tables.
    """
    all_routing_tables = {}
    for node in graph.nodes:
        all_routing_tables[node] = compute_spf_for_node(graph, node)
    return all_routing_tables
