```python
import json
import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from simulator import simulate


def main():
    """
    Runs the full network simulation and prints the results to the console.
    
    This function executes the network simulation and outputs the results
    in a formatted JSON structure. It also provides guidance on accessing
    the dashboard interface.
    
    Returns:
        int: Exit code (0 for success, 1 for failure)
    """
    print("Running network simulation...")
    
    try:
        results = simulate.simulate()
        
        # Pretty-print the JSON output
        print(json.dumps(results, indent=2))
        print("\nSimulation complete. Run 'python -m simulator.api' to see the dashboard.")
        
        return 0
        
    except Exception as e:
        print(f"Error during simulation: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc(file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
```