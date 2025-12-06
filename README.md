# Network Protocol Simulator: VXLAN + OSPF

A lightweight, self-contained Python project that **simulates OSPF routing** over a spine-leaf fabric and **models VXLAN overlays** with VTEPs and VNIs. No root privileges required and **no Mininet dependency** — this is a **logical simulator** for interview-ready demos.

## Features

- Build a small spine-leaf topology with configurable leaves and spines
- Run a simplified **OSPF** (link-state) process per router, compute SPF, and generate routing tables
- Define **VXLAN** segments (VNI), **VTEPs**, and logical L2 attachments; simulate encapsulation paths using underlay routes
- REST API + simple HTML dashboard to inspect topology, routes, and VXLAN tunnels
- CLI to run a full simulation and print results
- Pytest with basic route correctness checks

## Quickstart

```bash
# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run CLI simulation
python -m simulator.cli

# Start API server
python -m simulator.api
# Open http://127.0.0.1:5000 in your browser
```

## Project Layout

```
simulator/
  api.py           # Flask API and minimal dashboard
  cli.py           # CLI runner
  topology.py      # Nodes, Links, Fabric builder
  ospf.py          # OSPF LSDB + SPF + route installation
  vxlan.py         # VTEP, VNI, tunnel resolution
tests/
  test_spf.py      # SPF algorithm tests
README.md
requirements.txt
```

## Architecture

### Topology Layer
- Defines network nodes (routers, switches) and links
- Builds spine-leaf fabric with configurable parameters
- Manages link costs and adjacencies

### OSPF Layer
- Implements simplified link-state routing protocol
- Maintains Link State Database (LSDB) per router
- Computes shortest paths using Dijkstra's algorithm
- Installs routes in routing tables

### VXLAN Layer
- Models Virtual Extensible LAN overlay networks
- Manages VTEPs (VXLAN Tunnel Endpoints)
- Handles VNI (VXLAN Network Identifier) assignments
- Resolves tunnel paths using underlay routing

## Usage Examples

### CLI Simulation
```bash
# Run default simulation
python -m simulator.cli

# View topology and routing tables
python -m simulator.cli --verbose
```

### API Server
```bash
# Start server on default port (5000)
python -m simulator.api

# Access endpoints:
# GET /api/topology - View network topology
# GET /api/routes - View routing tables
# GET /api/vxlan - View VXLAN tunnels
```

## Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=simulator

# Run specific test file
pytest tests/test_spf.py
```

## Extending the Simulator

### Custom Topologies
Modify `topology.py` to:
- Adjust spine-leaf fabric size
- Change link costs and metrics
- Add custom node types

### VXLAN Enhancements
Extend `vxlan.py` to add:
- MAC address learning
- EVPN control-plane modeling
- Multi-tenancy support
- ARP suppression

### OSPF Features
Enhance `ospf.py` with:
- Area support
- LSA aging and refresh
- Designated Router election
- Route summarization

## Notes

- This is a **logical simulator**: it computes routes and tunnels rather than forwarding real packets
- No kernel networking or root privileges required
- Suitable for learning, demonstrations, and interview preparation
- Performance is optimized for small to medium topologies (< 100 nodes)

## Requirements

- Python 3.7+
- Flask (for API server)
- pytest (for testing)

See `requirements.txt` for complete dependency list.

## License

See LICENSE file for details.