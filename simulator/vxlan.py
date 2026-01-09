```python
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set, Tuple


@dataclass
class VTEP:
    """A VXLAN Tunnel End Point.
    
    Attributes:
        name: Unique identifier for the VTEP
        ip: IP address of the VTEP
        vnis: Set of VNI IDs this VTEP participates in
    """
    name: str
    ip: str
    vnis: Set[int] = field(default_factory=set)


@dataclass
class VNI:
    """A VXLAN Network Identifier, representing a virtual L2 segment.
    
    Attributes:
        id: Unique VNI identifier (24-bit value in real VXLAN)
        name: Human-readable name for the VNI
        members: Set of VTEP names that are members of this VNI
    """
    id: int
    name: str
    members: Set[str] = field(default_factory=set)


class VXLANOverlay:
    """Manages VXLAN overlay network with VTEPs and VNIs.
    
    This class provides the core functionality for managing a VXLAN overlay,
    including VTEP registration, VNI management, and tunnel enumeration.
    """

    def __init__(self) -> None:
        """Initialize an empty VXLAN overlay network."""
        self.vnis: Dict[int, VNI] = {}
        self.vteps: Dict[str, VTEP] = {}

    def add_vni(self, vni_id: int, name: str) -> None:
        """Add a VNI to the overlay if it doesn't already exist.
        
        Args:
            vni_id: The VNI identifier (should be 0-16777215 for valid VXLAN)
            name: The VNI name
        """
        if vni_id not in self.vnis:
            self.vnis[vni_id] = VNI(id=vni_id, name=name)

    def attach_vtep(self, node: str, ip: str, vnis: List[int]) -> None:
        """Attach a VTEP to the overlay and associate it with VNIs.
        
        Creates the VTEP if it doesn't exist, and automatically creates any
        VNIs that are not already present in the overlay. Updates the VTEP's
        IP address and VNI associations if it already exists.
        
        Args:
            node: The VTEP node name
            ip: The VTEP IP address
            vnis: List of VNI IDs to associate with this VTEP
        """
        if node not in self.vteps:
            self.vteps[node] = VTEP(name=node, ip=ip)
        else:
            # Update IP address if VTEP already exists
            self.vteps[node].ip = ip
        
        vtep = self.vteps[node]
        for vni_id in vnis:
            # Auto-create VNI if not present
            self.add_vni(vni_id, f"VNI-{vni_id}")
            self.vnis[vni_id].members.add(node)
            vtep.vnis.add(vni_id)

    def tunnels_for_vni(self, vni_id: int) -> List[Tuple[str, str]]:
        """Returns all VTEP-to-VTEP tunnels for a given VNI.
        
        Generates all unique pairs of VTEPs that are members of the specified VNI.
        Each pair represents a potential tunnel between two endpoints. The tunnels
        are returned in a consistent order (sorted by VTEP name).
        
        Args:
            vni_id: The VNI identifier
            
        Returns:
            List of tuples representing VTEP pairs that form tunnels.
            Returns empty list if VNI doesn't exist or has fewer than 2 members.
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
        and VXLAN header containing the VNI. This is a simplified simulation
        for educational purposes.
        
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
            "description": "VXLAN Encapsulation",
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

    def list_vteps(self) -> List[str]:
        """List all VTEP names in the overlay.
        
        Returns:
            Sorted list of VTEP names
        """
        return sorted(self.vteps.keys())

    def list_vnis(self) -> List[int]:
        """List all VNI IDs in the overlay.
        
        Returns:
            Sorted list of VNI IDs
        """
        return sorted(self.vnis.keys())
```