import argparse
import json
import os
import sys
import traceback

# Add the project root to the Python path so the package imports cleanly
# whether invoked as `python -m simulator.cli` or `python simulator/cli.py`.
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from simulator import simulate


def parse_vni(values):
    """Parse ``--vni ID:NAME`` options into a ``{id: name}`` mapping."""
    vnis = {}
    for item in values or []:
        if ":" in item:
            vid, name = item.split(":", 1)
        else:
            vid, name = item, f"VNI-{item}"
        vnis[int(vid)] = name
    return vnis or None


def print_summary(results):
    """Print a compact, human-readable summary of a simulation run."""
    topo = results["topology"]
    routes = results["routes"]
    vx = results["vxlan"]

    spines = [n["name"] for n in topo["nodes"] if n["role"] == "spine"]
    leaves = [n["name"] for n in topo["nodes"] if n["role"] == "leaf"]

    print("=" * 56)
    print("  VXLAN + OSPF Fabric Simulation")
    print("=" * 56)
    print(f"Spines ({len(spines)}): {', '.join(spines)}")
    print(f"Leaves ({len(leaves)}): {', '.join(leaves)}")
    print(f"Links      : {len(topo['links'])}")

    print("\nRouting tables (dest -> nexthop/cost):")
    for node in sorted(routes):
        entries = ", ".join(
            f"{dst} via {r['nexthop']}/{r['cost']}"
            for dst, r in sorted(routes[node].items())
        )
        print(f"  {node:<4}: {entries}")

    print("\nVXLAN overlay:")
    for vni_id, vni in vx["vnis"].items():
        members = ", ".join(vni["members"])
        print(f"  VNI {vni_id} ({vni['name']}): {members}")
        for a, b in vx["tunnels"].get(vni_id, vx["tunnels"].get(str(vni_id), [])):
            print(f"      tunnel {a} <-> {b}")

    if vx["sample_encapsulation"]:
        print("\nSample VXLAN encapsulation:")
        for k, v in vx["sample_encapsulation"].items():
            print(f"  {k}: {v}")
    print("=" * 56)


def main():
    """Run the network simulation and print the results.

    Returns:
        int: Exit code (0 for success, 1 for failure).
    """
    parser = argparse.ArgumentParser(
        description="Simulate OSPF routing and VXLAN overlays on a spine-leaf fabric."
    )
    parser.add_argument("--spines", type=int, default=2, help="Number of spine switches (default: 2)")
    parser.add_argument("--leaves", type=int, default=3, help="Number of leaf switches (default: 3)")
    parser.add_argument(
        "--vni",
        action="append",
        metavar="ID:NAME",
        help="VNI to provision, e.g. --vni 10010:customers-A (repeatable)",
    )
    parser.add_argument("--json", action="store_true", help="Print raw JSON instead of a summary")
    parser.add_argument("--verbose", action="store_true", help="Print both the summary and raw JSON")
    args = parser.parse_args()

    try:
        results = simulate.simulate(
            spines=args.spines,
            leaves=args.leaves,
            vnis=parse_vni(args.vni),
        )

        if args.json:
            print(json.dumps(results, indent=2))
        else:
            print_summary(results)
            if args.verbose:
                print("\nRaw JSON:")
                print(json.dumps(results, indent=2))

        print("\nTip: run 'python -m simulator.api' for the web dashboard.")
        return 0

    except Exception as e:
        print(f"Error during simulation: {e}", file=sys.stderr)
        traceback.print_exc(file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
