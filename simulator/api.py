```python
import sys
import os
from flask import Flask, render_template_string, jsonify

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from simulator import simulate

app = Flask(__name__)

# Run simulation once on startup
RESULTS = simulate.simulate()

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>VXLAN+OSPF Simulator</title>
    <style>
        body { 
            font-family: sans-serif; 
            margin: 2em; 
            background: #f9f9f9; 
        }
        h1, h2 { 
            color: #333; 
            border-bottom: 2px solid #eee; 
            padding-bottom: 5px; 
        }
        pre { 
            background: #fff; 
            border: 1px solid #ddd; 
            padding: 1em; 
            border-radius: 5px; 
            white-space: pre-wrap; 
            word-wrap: break-word;
            font-size: 14px; 
            overflow-x: auto;
        }
        .container { 
            display: grid; 
            grid-template-columns: 1fr 1fr; 
            gap: 2em; 
        }
        .col { 
            min-width: 0; 
        }
        nav { 
            margin-bottom: 2em; 
        }
        nav a { 
            margin-right: 1em; 
            text-decoration: none; 
            color: #007bff; 
        }
        nav a:hover {
            text-decoration: underline;
        }
        @media (max-width: 768px) {
            .container {
                grid-template-columns: 1fr;
            }
        }
    </style>
</head>
<body>
    <h1>VXLAN+OSPF Network Simulator</h1>
    <nav>
        <a href="/api/topology" target="_blank">API: Topology</a>
        <a href="/api/routes" target="_blank">API: Routes</a>
        <a href="/api/vxlan" target="_blank">API: VXLAN</a>
    </nav>
    
    <div class="container">
        <div class="col">
            <h2>Topology</h2>
            <pre id="topology"></pre>
            
            <h2>VXLAN Details</h2>
            <pre id="vxlan"></pre>
        </div>
        <div class="col">
            <h2>Routing Tables</h2>
            <pre id="routes"></pre>
        </div>
    </div>

    <script>
        // Pretty-print JSON into the <pre> tags
        document.getElementById('topology').textContent = JSON.stringify({{ topology | tojson }}, null, 2);
        document.getElementById('routes').textContent = JSON.stringify({{ routes | tojson }}, null, 2);
        document.getElementById('vxlan').textContent = JSON.stringify({{ vxlan | tojson }}, null, 2);
    </script>
</body>
</html>
"""


@app.route("/")
def dashboard():
    """Renders the main dashboard with simulation results."""
    return render_template_string(
        HTML_TEMPLATE,
        topology=RESULTS.get("topology", {}),
        routes=RESULTS.get("routes", {}),
        vxlan=RESULTS.get("vxlan", {})
    )


@app.route("/api/topology")
def api_topology():
    """Returns the network topology as JSON."""
    return jsonify(RESULTS.get("topology", {}))


@app.route("/api/routes")
def api_routes():
    """Returns the routing tables as JSON."""
    return jsonify(RESULTS.get("routes", {}))


@app.route("/api/vxlan")
def api_vxlan():
    """Returns the VXLAN configuration as JSON."""
    return jsonify(RESULTS.get("vxlan", {}))


if __name__ == "__main__":
    print("Starting Flask server at http://127.0.0.1:5000")
    app.run(debug=True)
```