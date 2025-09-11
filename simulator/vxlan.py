from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Set, Tuple

@dataclass
class VTEP:
    """A VXLAN Tunnel End Point."""
    name: str
    ip: str
    vnis: Set[int] = field(default_factory=set)

@dataclass
class VNI:
    """A VXLAN Network Identifier, representing a virtual L2 segment."""
    id: int
    name: str
    members: Set[str] = field(default_factory=set) # Set of VTEP names

class VXLANOverlay:
    def __init__(self):
        self.vnis: Dict[int, VNI] = {}
        self.vteps: Dict[str, VTEP] = {}

    def add_vni(self, id: int, name: str):
        if id not in self.vnis:
            self.vnis[id] = VNI(id=id, name=name)

    def attach_vtep(self, node: str, ip: str, vnis: List[int]):
        if node not in self.vteps:
            self.vteps[node] = VTEP(name=node, ip=ip)
        
        for vni_id in vnis:
            self.add_vni(vni_id, f"VNI-{vni_id}") # Auto-create VNI if not present
            self.vnis[vni_id].members.add(node)
            self.vteps[node].vnis.add(vni_id)

    def tunnels_for_vni(self, vni_id: int) -> List[Tuple[str, str]]:
        """Returns all VTEP-to-VTEP tunnels for a given VNI."""
        if vni_id not in self.vnis:
            return []
        
        members = list(self.vnis[vni_id].members)
        tunnels = []
        for i in range(len(members)):
            for j in range(i + 1, len(members)):
                tunnels.append((members[i], members[j]))
        return tunnels

    def encapsulate(self, vtep_a: VTEP, vtep_b: VTEP, vni_id: int, payload_desc: str) -> Dict:
        """Simulates the VXLAN encapsulation of a payload."""
        return {
            "description": "Example VXLAN Encapsulation",
            "payload": payload_desc,
            "vxlan_header": f"VNI {vni_id}",
            "outer_udp_header": "UDP Port 4789",
            "outer_ip_header": f"src={vtep_a.ip}, dst={vtep_b.ip}",
        }
