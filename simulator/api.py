import os
import sys

from flask import Flask, jsonify, render_template_string, request

# Add the project root to the Python path.
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from simulator import simulate

app = Flask(__name__)

# Run the default simulation once on startup.
RESULTS = simulate.simulate()

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>VXLAN + OSPF Simulator</title>
    <style>
        :root {
            --bg: #0f172a;
            --panel: #1e293b;
            --border: #334155;
            --text: #e2e8f0;
            --muted: #94a3b8;
            --spine: #f59e0b;
            --leaf: #38bdf8;
            --accent: #a78bfa;
        }
        * { box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            margin: 0; padding: 2em; background: var(--bg); color: var(--text);
        }
        h1 { margin: 0 0 .2em; font-size: 1.6em; }
        .sub { color: var(--muted); margin-bottom: 1.5em; }
        h2 { font-size: 1.05em; margin: 0 0 .6em; color: var(--text); }
        nav { margin-bottom: 1.5em; display: flex; gap: 1em; flex-wrap: wrap; }
        nav a {
            text-decoration: none; color: var(--accent); font-weight: 500;
            border: 1px solid var(--border); padding: .35em .8em; border-radius: 6px;
        }
        nav a:hover { background: var(--panel); }
        .grid { display: grid; grid-template-columns: 1fr 1fr; gap: 1.5em; }
        .panel {
            background: var(--panel); border: 1px solid var(--border);
            border-radius: 10px; padding: 1.2em; min-width: 0;
        }
        .wide { grid-column: 1 / -1; }
        pre {
            margin: 0; white-space: pre-wrap; word-wrap: break-word;
            font-family: 'SFMono-Regular', Consolas, 'Courier New', monospace;
            font-size: 13px; line-height: 1.5; color: var(--text);
            max-height: 340px; overflow: auto;
        }
        .legend { display: flex; gap: 1.2em; font-size: .85em; color: var(--muted); margin-top: .6em; }
        .dot { display: inline-block; width: 10px; height: 10px; border-radius: 50%; margin-right: 5px; }
        @media (max-width: 820px) { .grid { grid-template-columns: 1fr; } body { padding: 1em; } }
    </style>
</head>
<body>
    <h1>VXLAN + OSPF Network Simulator</h1>
    <div class="sub">Spine-leaf fabric · OSPF SPF routing · VXLAN overlay tunnels</div>
    <nav>
        <a href="/api/topology" target="_blank">API: Topology</a>
        <a href="/api/routes" target="_blank">API: Routes</a>
        <a href="/api/vxlan" target="_blank">API: VXLAN</a>
        <a href="/api/simulate?spines=2&leaves=4" target="_blank">API: Custom sim</a>
    </nav>

    <div class="grid">
        <div class="panel wide">
            <h2>Fabric Topology</h2>
            <div id="diagram"></div>
            <div class="legend">
                <span><span class="dot" style="background: var(--spine)"></span>Spine</span>
                <span><span class="dot" style="background: var(--leaf)"></span>Leaf (VTEP)</span>
            </div>
        </div>
        <div class="panel">
            <h2>Routing Tables (OSPF SPF)</h2>
            <pre id="routes"></pre>
        </div>
        <div class="panel">
            <h2>VXLAN Overlay</h2>
            <pre id="vxlan"></pre>
        </div>
    </div>

    <script>
        const topology = {{ topology | tojson }};
        const routes = {{ routes | tojson }};
        const vxlan = {{ vxlan | tojson }};

        document.getElementById('routes').textContent = JSON.stringify(routes, null, 2);
        document.getElementById('vxlan').textContent = JSON.stringify(vxlan, null, 2);

        // Render the spine-leaf fabric as an SVG diagram.
        function renderDiagram(topo) {
            const spines = topo.nodes.filter(n => n.role === 'spine');
            const leaves = topo.nodes.filter(n => n.role === 'leaf');
            const W = 720, H = 300, padX = 60;
            const pos = {};
            const place = (arr, y) => arr.forEach((n, i) => {
                const x = arr.length === 1 ? W / 2 : padX + i * (W - 2 * padX) / (arr.length - 1);
                pos[n.name] = { x, y, role: n.role, vtep: n.vtep_ip };
            });
            place(spines, 60);
            place(leaves, 230);

            const NS = 'http://www.w3.org/2000/svg';
            const svg = document.createElementNS(NS, 'svg');
            svg.setAttribute('viewBox', `0 0 ${W} ${H}`);
            svg.setAttribute('width', '100%');

            topo.links.forEach(l => {
                const a = pos[l.a], b = pos[l.b];
                if (!a || !b) return;
                const line = document.createElementNS(NS, 'line');
                line.setAttribute('x1', a.x); line.setAttribute('y1', a.y);
                line.setAttribute('x2', b.x); line.setAttribute('y2', b.y);
                line.setAttribute('stroke', '#475569');
                line.setAttribute('stroke-width', '1.5');
                svg.appendChild(line);
            });

            Object.entries(pos).forEach(([name, p]) => {
                const g = document.createElementNS(NS, 'g');
                const rect = document.createElementNS(NS, 'rect');
                const w = 68, h = 34;
                rect.setAttribute('x', p.x - w / 2); rect.setAttribute('y', p.y - h / 2);
                rect.setAttribute('width', w); rect.setAttribute('height', h);
                rect.setAttribute('rx', 7);
                rect.setAttribute('fill', p.role === 'spine' ? '#f59e0b' : '#38bdf8');
                g.appendChild(rect);
                const label = document.createElementNS(NS, 'text');
                label.setAttribute('x', p.x); label.setAttribute('y', p.y + 4);
                label.setAttribute('text-anchor', 'middle');
                label.setAttribute('font-size', '14');
                label.setAttribute('font-weight', '700');
                label.setAttribute('fill', '#0f172a');
                label.textContent = name;
                g.appendChild(label);
                if (p.vtep) {
                    const vt = document.createElementNS(NS, 'text');
                    vt.setAttribute('x', p.x); vt.setAttribute('y', p.y + 30);
                    vt.setAttribute('text-anchor', 'middle');
                    vt.setAttribute('font-size', '10');
                    vt.setAttribute('fill', '#94a3b8');
                    vt.textContent = 'VTEP ' + p.vtep;
                    g.appendChild(vt);
                }
                svg.appendChild(g);
            });
            const box = document.getElementById('diagram');
            box.innerHTML = '';
            box.appendChild(svg);
        }
        renderDiagram(topology);
    </script>
</body>
</html>
"""


@app.route("/")
def dashboard():
    """Render the main dashboard with the default simulation results."""
    return render_template_string(
        HTML_TEMPLATE,
        topology=RESULTS.get("topology", {}),
        routes=RESULTS.get("routes", {}),
        vxlan=RESULTS.get("vxlan", {}),
    )


@app.route("/api/topology")
def api_topology():
    """Return the network topology as JSON."""
    return jsonify(RESULTS.get("topology", {}))


@app.route("/api/routes")
def api_routes():
    """Return the routing tables as JSON."""
    return jsonify(RESULTS.get("routes", {}))


@app.route("/api/vxlan")
def api_vxlan():
    """Return the VXLAN configuration as JSON."""
    return jsonify(RESULTS.get("vxlan", {}))


@app.route("/api/simulate")
def api_simulate():
    """Run a simulation with custom dimensions from query params.

    Query params:
        spines: number of spine switches (default 2)
        leaves: number of leaf switches (default 3)
    """
    spines = request.args.get("spines", default=2, type=int)
    leaves = request.args.get("leaves", default=3, type=int)
    return jsonify(simulate.simulate(spines=spines, leaves=leaves))


if __name__ == "__main__":
    print("Starting Flask server at http://127.0.0.1:5000")
    app.run(debug=True, host="127.0.0.1", port=5000)
