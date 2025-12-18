```python
from __future__ import annotations
from typing import TYPE_CHECKING, Dict, Tuple
import networkx as nx

if TYPE_CHECKING:
    from .topology import Fabric


def compute_spf_for_node(graph: nx.Graph, start_node: str) -> Dict[str, Tuple[str, int]]:
    """
    Computes Shortest Path First (Dijkstra's algorithm) for a single node.
    
    Args:
        graph: NetworkX graph representing the network topology
        start_node: Source node identifier for SPF computation
    
    Returns:
        Routing table mapping destination nodes to (next_hop, cost) tuples.
        The start_node itself is excluded from the routing table.
    """
    if start_node not in graph:
        return {}
    
    # Compute shortest paths and costs using Dijkstra's algorithm
    paths = nx.single_source_dijkstra_path(graph, start_node, weight="cost")
    costs = nx.single_source_dijkstra_path_length(graph, start_node, weight="cost")
    
    routing_table = {}
    for dest, path in paths.items():
        # Skip the source node itself
        if start_node == dest:
            continue
        
        # Determine next hop: second node in path for multi-hop, or destination if directly connected
        next_hop = path[1] if len(path) > 1 else dest
        routing_table[dest] = (next_hop, costs[dest])
    
    return routing_table


def install_routes_for_all(graph: nx.Graph) -> Dict[str, Dict[str, Tuple[str, int]]]:
    """
    Computes SPF for all nodes in the graph.
    
    Args:
        graph: NetworkX graph representing the network topology
    
    Returns:
        Dictionary mapping each node to its routing table.
        Each routing table maps destination nodes to (next_hop, cost) tuples.
    """
    all_routing_tables = {}
    for node in graph.nodes:
        all_routing_tables[node] = compute_spf_for_node(graph, node)
    return all_routing_tables
```