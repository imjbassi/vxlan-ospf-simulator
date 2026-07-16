from __future__ import annotations
from typing import Any, Dict, List, Optional

from . import ospf, topology, vxlan


def build_fabric(spines: int = 2, leaves: int = 3) -> topology.Fabric:
    """Build a spine-leaf fabric with the requested dimensions.

    Args:
        spines: Number of spine switches.
        leaves: Number of leaf switches.

    Returns:
        Fabric: The constructed fabric topology.
    """
    return topology.Fabric().build_spine_leaf(spines=spines, leaves=leaves)


def build_overlay(
    fabric: topology.Fabric,
    vnis: Optional[Dict[int, str]] = None,
) -> vxlan.VXLANOverlay:
    """Build a VXLAN overlay on top of the given fabric.

    Every leaf that has a VTEP IP is attached to each requested VNI.

    Args:
        fabric: The underlying fabric topology.
        vnis: Mapping of VNI id -> friendly name. Defaults to ``{10010: "customers-A"}``.

    Returns:
        VXLANOverlay: The configured VXLAN overlay.
    """
    if vnis is None:
        vnis = {10010: "customers-A"}

    vx = vxlan.VXLANOverlay()
    for vni_id, name in vnis.items():
        vx.add_vni(vni_id, name)

    vni_ids = list(vnis.keys())
    for name, node in fabric.nodes.items():
        if node.role == "leaf" and node.vtep_ip:
            vx.attach_vtep(node=name, ip=node.vtep_ip, vnis=vni_ids)

    return vx


def simulate(
    spines: int = 2,
    leaves: int = 3,
    vnis: Optional[Dict[int, str]] = None,
) -> Dict[str, Any]:
    """Run a full simulation: build the fabric, run OSPF, and set up VXLAN.

    Args:
        spines: Number of spine switches.
        leaves: Number of leaf switches.
        vnis: Mapping of VNI id -> friendly name. Defaults to ``{10010: "customers-A"}``.

    Returns:
        Dict containing topology, routing tables, and VXLAN configuration.
    """
    if vnis is None:
        vnis = {10010: "customers-A"}

    # Build the fabric topology.
    fabric = build_fabric(spines=spines, leaves=leaves)

    # Compute OSPF routes for every node and install them.
    rtab = ospf.install_routes_for_all(fabric.graph)
    for name, node in fabric.nodes.items():
        node.routes = rtab[name]

    # Build the VXLAN overlay and enumerate tunnels per VNI.
    overlay = build_overlay(fabric, vnis)
    tunnels: Dict[int, List[List[str]]] = {
        vni_id: [list(pair) for pair in overlay.tunnels_for_vni(vni_id)]
        for vni_id in overlay.list_vnis()
    }

    # Produce a sample encapsulation from the first available tunnel.
    sample = None
    for vni_id, pairs in tunnels.items():
        if pairs:
            src_vtep, dst_vtep = pairs[0]
            sample = overlay.encapsulate(
                overlay.vteps[src_vtep],
                overlay.vteps[dst_vtep],
                vni_id,
                payload_desc="L2 frame: MAC A -> MAC B",
            )
            break

    return {
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
                vni_id: {"name": vni.name, "members": sorted(vni.members)}
                for vni_id, vni in overlay.vnis.items()
            },
            "vteps": {
                vtep_name: {"ip": vtep.ip, "vnis": sorted(vtep.vnis)}
                for vtep_name, vtep in overlay.vteps.items()
            },
            "tunnels": tunnels,
            "sample_encapsulation": sample,
        },
    }


if __name__ == "__main__":
    import json

    print(json.dumps(simulate(), indent=2))
