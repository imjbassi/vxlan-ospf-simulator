```python
import pytest
from simulator import ospf, topology


def test_spf_costs_and_paths():
    """
    Builds a simple 2x2 fabric and verifies SPF results.
    
    Tests:
    - Leaf-to-leaf cost (through spine): 20
    - Leaf-to-spine cost (direct): 10
    - Next-hop selection for multi-path scenarios
    - Path symmetry
    """
    fab = topology.Fabric().build_spine_leaf(spines=2, leaves=2)
    rtab = ospf.install_routes_for_all(fab.graph)

    # Cost from leaf to leaf should be 20 (leaf -> spine -> leaf)
    assert rtab["L1"]["L2"][1] == 20, "Leaf-to-leaf cost should be 20"
    
    # Next-hop from L1 to L2 should be one of the spines
    assert rtab["L1"]["L2"][0] in ["S1", "S2"], "Next-hop should be a spine"

    # Cost from leaf to spine is 10 (direct link)
    assert rtab["L1"]["S1"][1] == 10, "Leaf-to-spine cost should be 10"
    assert rtab["L1"]["S1"][0] == "S1", "Next-hop to S1 should be S1 itself"

    # Symmetric paths: cost from L1 to L2 equals cost from L2 to L1
    assert rtab["L1"]["L2"][1] == rtab["L2"]["L1"][1], "Paths should be symmetric"
```