```python
from __future__ import annotations
from typing import Dict, Optional, Any
from . import topology, ospf, vxlan


def build_demo_fabric() -> topology.Fabric:
    """
    Build a demo spine-leaf fabric with 2 spines and 3 leaves.
    
    Returns:
        Fabric: The constructed fabric topology.
    """
    fabric = topology.Fabric().build_spine_leaf(spines=2, leaves=3)
    return fabric


def build_overlay(fabric: topology.Fabric) -> vxlan.VXLANOverlay:
    """
    Build a VXLAN overlay on top of the given fabric.
    
    Attaches all leaf nodes with VTEP IPs to VNI 10010.
    
    Args:
        fabric: The underlying fabric topology.
        
    Returns:
        VXLANOverlay: The configured VXLAN overlay.
    """
    vx = vxlan.VXLANOverlay()
    vx.add_vni(10010, "customers-A")
    
    # Attach all leaves as VTEPs to VNI 10010
    for name, node in fabric.nodes.items():
        if node.role == "leaf" and node.vtep_ip:
            vx.attach_vtep(node=name, ip=node.vtep_ip, vnis=[10010])
    
    return vx


def simulate() -> Dict[str, Any]:
    """
    Run a basic simulation with demo fabric and VXLAN overlay.
    
    Returns:
        Dict containing topology, routes, and VXLAN configuration.
    """
    # Build the fabric topology
    fabric = build_demo_fabric()
    
    # Compute OSPF routes for all nodes
    rtab = ospf.install_routes_for_all(fabric.graph)
    for name, node in fabric.nodes.items():
        node.routes = rtab[name]

    # Build VXLAN overlay
    overlay = build_overlay(fabric)
    tunnels = overlay.tunnels_for_vni(10010)

    # Generate a sample encapsulation if tunnels exist
    sample = None
    if tunnels:
        src_vtep, dst_vtep = tunnels[0]
        src_vtep_obj = overlay.vteps[src_vtep]
        dst_vtep_obj = overlay.vteps[dst_vtep]
        sample = overlay.encapsulate(
            src_vtep_obj, dst_vtep_obj, 10010, payload_desc="L2 frame: MAC A -> MAC B"
        )

    result = {
        "topology": fabric.to_dict(),
        "routes": {
            node_name: {
                dst: {"nexthop": nexthop, "cost": cost}
                for dst, (nexthop, cost) in route_table.items()
            }
            for node_name, route_table in rtab.items()
        },
        "vxlan": {
            "vnis": {
                vni_id: {"name": vni.name, "members": list(vni.members)}
                for vni_id, vni in overlay.vnis.items()
            },
            "vteps": {
                vtep_name: {"ip": vtep.ip, "vnis": list(vtep.vnis)}
                for vtep_name, vtep in overlay.vteps.items()
            },
            "tunnels_vni_10010": tunnels,
            "sample_encapsulation": sample,
        },
    }
    return result


def run_full_simulation(
    num_spines: int = 2,
    num_leaves: int = 3,
    vni_config: Optional[Dict[int, list]] = None
) -> Dict[str, Any]:
    """
    Build the fabric, run OSPF, set up VXLAN, and return all results.
    
    Args:
        num_spines: Number of spine switches to create.
        num_leaves: Number of leaf switches to create.
        vni_config: Dictionary mapping VNI IDs to lists of leaf names.
                   If None, uses default configuration.
    
    Returns:
        Dict containing topology, routing tables, VXLAN configuration, and tunnels.
    """
    if vni_config is None:
        # Default VNI config: VNI 100 with all leaves, VNI 200 with a subset
        vni_config = {
            100: [f"leaf{i}" for i in range(1, num_leaves + 1)],
            200: [f"leaf{i}" for i in range(1, max(2, num_leaves // 2 + 1) + 1)],
        }

    # 1. Build the fabric topology
    fabric = topology.Fabric(num_spines, num_leaves)
    
    # 2. Run OSPF to compute routing tables
    routing_tables = ospf.compute_routing_tables(fabric)
    
    # 3. Set up the VXLAN overlay
    vteps, vnis = vxlan.setup_vxlan_overlay(fabric, vni_config)
    
    # 4. Compute VXLAN tunnels based on underlay routes
    tunnels = vxlan.compute_vxlan_tunnels(vnis, routing_tables)
    
    # 5. Simulate a sample encapsulation
    example_encap = None
    if tunnels.get(100) and len(tunnels[100]) > 0:
        # Find two VTEPs in VNI 100 to show an example
        vtep1_name = tunnels[100][0]["from"]
        vtep2_name = tunnels[100][0]["to"]
        if vtep1_name in vteps and vtep2_name in vteps:
            vtep1 = vteps[vtep1_name]
            vtep2 = vteps[vtep2_name]
            example_encap = vxlan.simulate_encapsulation(vtep1, vtep2, 100)

    return {
        "topology": fabric.get_topology(),
        "routing_tables": routing_tables,
        "vxlan_vteps": {
            name: str(vtep.ip_address) for name, vtep in vteps.items()
        },
        "vxlan_vnis": {
            vni_id: [member.name for member in vni.members]
            for vni_id, vni in vnis.items()
        },
        "vxlan_tunnels": tunnels,
        "example_encapsulation": example_encap,
    }


if __name__ == "__main__":
    import json
    print(json.dumps(simulate(), indent=2))
```