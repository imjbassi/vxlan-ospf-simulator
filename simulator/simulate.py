from __future__ import annotations
from typing import Dict, Tuple
from . import topology, ospf, vxlan

def build_demo_fabric():
    fabric = topology.Fabric().build_spine_leaf(spines=2, leaves=3)
    return fabric

def build_overlay(fabric: topology.Fabric):
    vx = vxlan.VXLANOverlay()
    vx.add_vni(10010, "customers-A")
    # Attach all leaves as VTEPs to VNI 10010
    for name, node in fabric.nodes.items():
        if node.role == "leaf" and node.vtep_ip:
            vx.attach_vtep(node=name, ip=node.vtep_ip, vnis=[10010])
    return vx

def simulate():
    fabric = build_demo_fabric()
    rtab = ospf.install_routes_for_all(fabric.graph)
    for name, node in fabric.nodes.items():
        node.routes = rtab[name]

    overlay = build_overlay(fabric)
    tunnels = overlay.tunnels_for_vni(10010)

    sample = None
    if tunnels:
        a, b = tunnels[0]
        va = overlay.vteps[a]
        vb = overlay.vteps[b]
        sample = overlay.encapsulate(va, vb, 10010, payload_desc="L2 frame: MAC A -> MAC B")

    result = {
        "topology": fabric.to_dict(),
        "routes": {n: {dst: {"nexthop": nh, "cost": c} for dst, (nh, c) in tbl.items()} for n, tbl in rtab.items()},
        "vxlan": {
            "vnis": {vid: {"name": v.name, "members": list(v.members)} for vid, v in overlay.vnis.items()},
            "vteps": {n: {"ip": v.ip, "vnis": list(v.vnis)} for n, v in overlay.vteps.items()},
            "tunnels_vni_10010": tunnels,
            "sample_encapsulation": sample,
        },
    }
    return result

def run_full_simulation(num_spines=2, num_leaves=3, vni_config=None):
    """
    Builds the fabric, runs OSPF, sets up VXLAN, and returns all results.
    """
    if vni_config is None:
        # Default VNI config: VNI 100 with all leaves, VNI 200 with a subset.
        vni_config = {
            100: [f"leaf{i}" for i in range(1, num_leaves + 1)],
            200: [f"leaf{i}" for i in range(1, num_leaves // 2 + 1)],
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
        "vxlan_vteps": {name: str(vtep.ip_address) for name, vtep in vteps.items()},
        "vxlan_vnis": {vni_id: [m.name for m in vni.members] for vni_id, vni in vnis.items()},
        "vxlan_tunnels": tunnels,
        "example_encapsulation": example_encap,
    }

if __name__ == "__main__":
    import json
    print(json.dumps(simulate(), indent=2))
