from simulator import simulate, vxlan


def test_tunnels_are_full_mesh_between_members():
    """N VTEPs in a VNI yield N*(N-1)/2 unique tunnels."""
    vx = vxlan.VXLANOverlay()
    for i, name in enumerate(["L1", "L2", "L3", "L4"], start=1):
        vx.attach_vtep(node=name, ip=f"10.0.0.{i}", vnis=[10010])

    tunnels = vx.tunnels_for_vni(10010)
    assert len(tunnels) == 6  # 4 choose 2
    # No self-tunnels and no duplicates.
    assert all(a != b for a, b in tunnels)
    assert len(set(tunnels)) == len(tunnels)


def test_unknown_vni_has_no_tunnels():
    vx = vxlan.VXLANOverlay()
    assert vx.tunnels_for_vni(999) == []


def test_encapsulation_carries_vni_and_endpoints():
    vx = vxlan.VXLANOverlay()
    vx.attach_vtep("L1", "10.0.0.1", [10010])
    vx.attach_vtep("L2", "10.0.0.2", [10010])
    pkt = vx.encapsulate(vx.vteps["L1"], vx.vteps["L2"], 10010, "frame")
    assert pkt["vxlan_header"] == "VNI 10010"
    assert "10.0.0.1" in pkt["outer_ip_header"]
    assert "10.0.0.2" in pkt["outer_ip_header"]


def test_simulate_end_to_end():
    """The full simulate() pipeline produces routes and overlay tunnels."""
    result = simulate.simulate(spines=2, leaves=3)
    assert len(result["topology"]["nodes"]) == 5
    assert len(result["topology"]["links"]) == 6
    # Every leaf pair should form a tunnel in the default VNI (3 leaves -> 3 tunnels).
    assert len(result["vxlan"]["tunnels"][10010]) == 3
    assert result["vxlan"]["sample_encapsulation"]["vxlan_header"] == "VNI 10010"
