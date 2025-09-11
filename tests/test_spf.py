import pytest
from simulator import ospf, topology

def test_spf_costs_and_paths():
    """
    Builds a simple 2x2 fabric and verifies SPF results.
    """
    fab = topology.Fabric().build_spine_leaf(spines=2, leaves=2)
    rtab = ospf.install_routes_for_all(fab.graph)

    # Cost from leaf to leaf should be 20 (leaf -> spine -> leaf)
    assert rtab["L1"]["L2"][1] == 20
    
    # Next-hop from L1 to L2 should be one of the spines
    assert rtab["L1"]["L2"][0] in ["S1", "S2"]

    # Cost from leaf to spine is 10
    assert rtab["L1"]["S1"][1] == 10
    assert rtab["L1"]["S1"][0] == "S1"

    # Symmetric paths
    assert rtab["L1"]["L2"][1] == rtab["L2"]["L1"][1]
