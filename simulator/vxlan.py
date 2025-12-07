```python
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
    members: Set[str] = field(default_factory=set)  # Set of VTEP names


class VXLANOverlay:
    """Manages VXLAN overlay network with VTEPs and VNIs."""

    def __init__(self):
        self.vnis: Dict[int, VNI] = {}
        self.vteps: Dict[str, VTEP] = {}

    def add_vni(self, id: int, name: str) -> None:
        """Add a VNI to the overlay if it doesn't already exist.
        
        Args:
            id: The VNI identifier
            name: The VNI name
        """
        if id not in self.vnis:
            self.vnis[id] = VNI(id=id, name=name)

    def attach_vtep(self, node: str, ip: str, vnis: List[int]) -> None:
        """Attach a VTEP to the overlay and associate it with VNIs.
        
        Args:
            node: The VTEP node name
            ip: The VTEP IP address
            vnis: List of VNI IDs to associate with this VTEP
        """
        if node not in self.vteps:
            self.vteps[node] = VTEP(name=node, ip=ip)
        
        for vni_id in vnis:
            # Auto-create VNI if not present
            self.add_vni(vni_id, f"VNI-{vni_id}")
            self.vnis[vni_id].members.add(node)
            self.vteps[node].vnis.add(vni_id)

    def tunnels_for_vni(self, vni_id: int) -> List[Tuple[str, str]]:
        """Returns all VTEP-to-VTEP tunnels for a given VNI.
        
        Args:
            vni_id: The VNI identifier
            
        Returns:
            List of tuples representing VTEP pairs that form tunnels
        """
        if vni_id not in self.vnis:
            return []
        
        members = list(self.vnis[vni_id].members)
        tunnels = []
        for i in range(len(members)):
            for j in range(i + 1, len(members)):
                tunnels.append((members[i], members[j]))
        return tunnels

    def encapsulate(self, vtep_a: VTEP, vtep_b: VTEP, vni_id: int, payload_desc: str) -> Dict:
        """Simulates the VXLAN encapsulation of a payload.
        
        Args:
            vtep_a: Source VTEP
            vtep_b: Destination VTEP
            vni_id: VNI identifier for the encapsulation
            payload_desc: Description of the payload being encapsulated
            
        Returns:
            Dictionary representing the encapsulated packet structure
        """
        return {
            "description": "Example VXLAN Encapsulation",
            "payload": payload_desc,
            "vxlan_header": f"VNI {vni_id}",
            "outer_udp_header": "UDP Port 4789",
            "outer_ip_header": f"src={vtep_a.ip}, dst={vtep_b.ip}",
        }
```