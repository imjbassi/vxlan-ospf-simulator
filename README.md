
# Network Protocol Simulator: VXLAN + OSPF (Skeleton)

A lightweight, self-contained Python project that **simulates OSPF routing** over a spine–leaf fabric and **models VXLAN overlays** with VTEPs and VNIs. No root privileges required and **no Mininet dependency** — this is a **logical simulator** for interview-ready demos.

## Features
- Build a small spine–leaf topology with configurable leaves and spines.
- Run a simplified **OSPF** (link-state) process per router, compute SPF, and generate routing tables.
- Define **VXLAN** segments (VNI), **VTEPs**, and logical L2 attachments; simulate encapsulation paths using underlay routes.
- REST API + simple HTML dashboard to inspect topology, routes, and VXLAN tunnels.
- CLI to run a full simulation and print results.
- Pytest with a basic route correctness check.

## Quickstart
```bash
python -m venv .venv
. .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# Run CLI simulation
python -m simulator.cli

# Start API server
python -m simulator.api
# Open http://127.0.0.1:5000
```

## Project Layout
```
simulator/
  api.py           # Flask API and minimal dashboard
  cli.py           # CLI runner
  topology.py      # Nodes, Links, Fabric builder
  ospf.py          # OSPF LSDB + SPF + route install
  vxlan.py         # VTEP, VNI, tunnel resolution
tests/
  test_spf.py
README.md
requirements.txt
```

## Notes
- This is a **logical simulator**: it computes routes/tunnels rather than forwarding real packets.
- Extend `topology.py` to change fabric size or link costs; extend `vxlan.py` to add MAC learning or EVPN control-plane modelling.
