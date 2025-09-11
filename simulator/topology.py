from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Tuple
import networkx as nx
import ipaddress

@dataclass
class Node:
    name: str
    role: str  # 'spine' | 'leaf' | 'host'
    loopback: str
    vtep_ip: str | None = None
    routes: Dict[str, Tuple[str, int]] = field(default_factory=dict)  # prefix -> (nexthop, cost)

    def __repr__(self):
        return f"Node({self.name}, {self.role})"

@dataclass
class Link:
    a: str
    b: str
    cost: int = 10

    def __repr__(self):
        return f"Link({self.a} <-> {self.b})"

class Fabric:
    def __init__(self):
        self.graph = nx.Graph()
        self.nodes: Dict[str, Node] = {}

    def add_node(self, node: Node):
        self.nodes[node.name] = node
        self.graph.add_node(node.name)

    def add_link(self, link: Link):
        self.graph.add_edge(link.a, link.b, cost=link.cost)

    def build_spine_leaf(self, spines=2, leaves=3) -> "Fabric":
        # Deterministic IP assignment helpers
        def loop(i): return f"10.255.0.{i}"
        def vtep(i): return f"10.0.0.{i}"

        # Add spines
        for i in range(1, spines + 1):
            name = f"S{i}"
            self.add_node(Node(name=name, role="spine", loopback=loop(i)))
        # Add leaves (with VTEPs)
        for i in range(1, leaves + 1):
            idx = i + spines
            name = f"L{i}"
            self.add_node(Node(name=name, role="leaf", loopback=loop(idx), vtep_ip=vtep(idx)))
        # Full-mesh spines to leaves
        for si in range(1, spines + 1):
            for li in range(1, leaves + 1):
                self.add_link(Link(a=f"S{si}", b=f"L{li}", cost=10))
        return self

    def neighbors(self, n: str) -> List[str]:
        return list(self.graph.neighbors(n))

    def link_cost(self, a: str, b: str) -> int:
        return self.graph[a][b]["cost"]

    def to_dict(self):
        return {
            "nodes": [
                {
                    "name": n.name,
                    "role": n.role,
                    "loopback": n.loopback,
                    "vtep_ip": n.vtep_ip,
                } for n in self.nodes.values()
            ],
            "links": [
                {"a": a, "b": b, "cost": data["cost"]}
                for a, b, data in self.graph.edges(data=True)
            ],
        }


