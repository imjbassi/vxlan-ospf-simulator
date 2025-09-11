import json
import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from simulator import simulate

def main():
    """
    Runs the full network simulation and prints the results to the console.
    """
    print("Running network simulation...")
    results = simulate.simulate()
    
    # Pretty-print the JSON output
    print(json.dumps(results, indent=2))
    print("\nSimulation complete. Run 'python -m simulator.api' to see the dashboard.")

if __name__ == "__main__":
    main()
