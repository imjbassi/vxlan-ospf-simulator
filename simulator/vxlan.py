```python
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Set, Tuple, Optional


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

    def __init__(self) -> None:
        """Initialize an empty VXLAN overlay network."""
        self.vnis: Dict[int, VNI] = {}
        self.vteps: Dict[str, VTEP] = {}

    def add_vni(self, vni_id: int, name: str) -> None:
        """Add a VNI to the overlay if it doesn't already exist.
        
        Args:
            vni_id: The VNI identifier
            name: The VNI name
        """
        if vni_id not in self.vnis:
            self.vnis[vni_id] = VNI(id=vni_id, name=name)

    def attach_vtep(self, node: str, ip: str, vnis: List[int]) -> None:
        """Attach a VTEP to the overlay and associate it with VNIs.
        
        Creates the VTEP if it doesn't exist, and automatically creates any
        VNIs that are not already present in the overlay.
        
        Args:
            node: The VTEP node name
            ip: The VTEP IP address
            vnis: List of VNI IDs to associate with this VTEP
        """
        if node not in self.vteps:
            self.vteps[node] = VTEP(name=node, ip=ip)
        
        vtep = self.vteps[node]
        for vni_id in vnis:
            # Auto-create VNI if not present
            self.add_vni(vni_id, f"VNI-{vni_id}")
            self.vnis[vni_id].members.add(node)
            vtep.vnis.add(vni_id)

    def tunnels_for_vni(self, vni_id: int) -> List[Tuple[str, str]]:
        """Returns all VTEP-to-VTEP tunnels for a given VNI.
        
        Generates all unique pairs of VTEPs that are members of the specified VNI.
        Each pair represents a potential tunnel between two endpoints.
        
        Args:
            vni_id: The VNI identifier
            
        Returns:
            List of tuples representing VTEP pairs that form tunnels.
            Returns empty list if VNI doesn't exist.
        """
        if vni_id not in self.vnis:
            return []
        
        members = sorted(self.vnis[vni_id].members)
        tunnels = []
        for i in range(len(members)):
            for j in range(i + 1, len(members)):
                tunnels.append((members[i], members[j]))
        return tunnels

    def encapsulate(
        self, 
        vtep_a: VTEP, 
        vtep_b: VTEP, 
        vni_id: int, 
        payload_desc: str
    ) -> Dict[str, str]:
        """Simulates the VXLAN encapsulation of a payload.
        
        Creates a representation of a VXLAN packet with outer IP/UDP headers
        and VXLAN header containing the VNI.
        
        Args:
            vtep_a: Source VTEP
            vtep_b: Destination VTEP
            vni_id: VNI identifier for the encapsulation
            payload_desc: Description of the payload being encapsulated
            
        Returns:
            Dictionary representing the encapsulated packet structure with
            payload, VXLAN header, UDP header, and outer IP header.
        """
        return {
            "description": "Example VXLAN Encapsulation",
            "payload": payload_desc,
            "vxlan_header": f"VNI {vni_id}",
            "outer_udp_header": "UDP Port 4789",
            "outer_ip_header": f"src={vtep_a.ip}, dst={vtep_b.ip}",
        }

    def get_vtep(self, name: str) -> Optional[VTEP]:
        """Retrieve a VTEP by name.
        
        Args:
            name: The VTEP name
            
        Returns:
            The VTEP object if found, None otherwise
        """
        return self.vteps.get(name)

    def get_vni(self, vni_id: int) -> Optional[VNI]:
        """Retrieve a VNI by ID.
        
        Args:
            vni_id: The VNI identifier
            
        Returns:
            The VNI object if found, None otherwise
        """
        return self.vnis.get(vni_id)
```