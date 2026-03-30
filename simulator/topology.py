```python
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional
import networkx as nx


@dataclass
class Node:
    """Represents a network node in the fabric topology.
    
    Attributes:
        name: Unique identifier for the node
        role: Node type - 'spine', 'leaf', or 'host'
        loopback: Loopback IP address for the node
        vtep_ip: VXLAN Tunnel Endpoint IP (only for leaf nodes)
        routes: Routing table mapping prefixes to (nexthop, cost) tuples
    """
    name: str
    role: str  # 'spine' | 'leaf' | 'host'
    loopback: str
    vtep_ip: Optional[str] = None
    routes: Dict[str, Tuple[str, int]] = field(default_factory=dict)  # prefix -> (nexthop, cost)

    def __repr__(self) -> str:
        return f"Node({self.name}, {self.role})"


@dataclass
class Link:
    """Represents a bidirectional link between two nodes.
    
    Attributes:
        a: Name of the first node
        b: Name of the second node
        cost: OSPF cost/metric for the link (default: 10)
    """
    a: str
    b: str
    cost: int = 10

    def __repr__(self) -> str:
        return f"Link({self.a} <-> {self.b})"


class Fabric:
    """Represents a network fabric topology with nodes and links.
    
    Uses NetworkX for graph operations and maintains a registry of nodes.
    Supports building spine-leaf topologies and querying topology properties.
    """
    
    def __init__(self) -> None:
        """Initialize an empty fabric topology."""
        self.graph: nx.Graph = nx.Graph()
        self.nodes: Dict[str, Node] = {}

    def add_node(self, node: Node) -> None:
        """Add a node to the fabric topology.
        
        Args:
            node: Node instance to add
        """
        self.nodes[node.name] = node
        self.graph.add_node(node.name)

    def add_link(self, link: Link) -> None:
        """Add a link between two nodes in the fabric.
        
        Args:
            link: Link instance defining the connection
        """
        self.graph.add_edge(link.a, link.b, cost=link.cost)

    def build_spine_leaf(self, spines: int = 2, leaves: int = 3) -> Fabric:
        """Build a standard spine-leaf topology with full-mesh connectivity.
        
        Creates a Clos network where all spine nodes connect to all leaf nodes.
        Spines are named S1, S2, ... and leaves are named L1, L2, ...
        Loopback IPs are assigned sequentially starting from 10.255.0.1.
        VTEP IPs for leaves are assigned starting from 10.0.0.{spine_count+1}.
        
        Args:
            spines: Number of spine nodes to create (default: 2)
            leaves: Number of leaf nodes to create (default: 3)
            
        Returns:
            Self for method chaining
        """
        # Deterministic IP assignment helpers
        def loopback_ip(i: int) -> str:
            """Generate loopback IP for node index i."""
            return f"10.255.0.{i}"
        
        def vtep_ip(i: int) -> str:
            """Generate VTEP IP for node index i."""
            return f"10.0.0.{i}"

        # Add spine nodes
        for i in range(1, spines + 1):
            name = f"S{i}"
            self.add_node(Node(name=name, role="spine", loopback=loopback_ip(i)))
        
        # Add leaf nodes with VTEP IPs
        for i in range(1, leaves + 1):
            idx = i + spines
            name = f"L{i}"
            self.add_node(Node(
                name=name,
                role="leaf",
                loopback=loopback_ip(idx),
                vtep_ip=vtep_ip(idx)
            ))
        
        # Create full-mesh connectivity between spines and leaves
        for si in range(1, spines + 1):
            for li in range(1, leaves + 1):
                self.add_link(Link(a=f"S{si}", b=f"L{li}", cost=10))
        
        return self

    def neighbors(self, node_name: str) -> List[str]:
        """Get all neighboring nodes for a given node.
        
        Args:
            node_name: Name of the node to query
            
        Returns:
            List of neighbor node names
            
        Raises:
            nx.NetworkXError: If node_name is not in the graph
        """
        return list(self.graph.neighbors(node_name))

    def link_cost(self, a: str, b: str) -> int:
        """Get the cost/metric of a link between two nodes.
        
        Args:
            a: Name of the first node
            b: Name of the second node
            
        Returns:
            Link cost as an integer
            
        Raises:
            KeyError: If the link does not exist
        """
        return self.graph[a][b]["cost"]

    def to_dict(self) -> Dict:
        """Serialize the fabric topology to a dictionary.
        
        Returns:
            Dictionary containing nodes and links with their attributes.
            Format:
                {
                    "nodes": [{"name": str, "role": str, "loopback": str, "vtep_ip": str|None}, ...],
                    "links": [{"a": str, "b": b, "cost": int}, ...]
                }
        """
        return {
            "nodes": [
                {
                    "name": node.name,
                    "role": node.role,
                    "loopback": node.loopback,
                    "vtep_ip": node.vtep_ip,
                }
                for node in self.nodes.values()
            ],
            "links": [
                {"a": a, "b": b, "cost": data["cost"]}
                for a, b, data in self.graph.edges(data=True)
            ],
        }
```