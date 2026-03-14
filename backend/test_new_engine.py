import asyncio
import sys
import os

# Set CWD to the project root if it isn't already
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(project_root, 'backend'))

from routing_engine import RoutingEngine
from signal_controller import SignalController
from simulation.engine import engine

async def test_engine_and_signals():
    re = RoutingEngine()
    
    # Mock data for testing (Majestic to Silk Board)
    origin = {'lat': 12.9716, 'lng': 77.5946}
    destination = {'lat': 12.9268, 'lng': 77.5951}
    
    print("Fetching route...")
    route_data = re.get_route(origin, destination)
    
    if "error" in route_data:
        print(f"Error: {route_data['error']}")
        # Fallback to mock if API key is missing or invalid
        route_data = re._get_mock_route(origin, destination)

    points = route_data.get("decoded_points", [])
    steps = route_data.get("steps", [])
    
    print(f"Initializing signals for route with {len(points)} points...")
    engine.set_route(points, steps)
    
    signals = engine.get_signals()
    junction_count = len(signals) // 3
    print(f"Total Signals: {len(signals)} ({junction_count} junctions)")
    
    if 2 <= junction_count <= 5:
        print("SUCCESS: Signal count is within 2-5 junctions range.")
    else:
        print(f"FAILURE: Signal count {junction_count} is OUTSIDE 2-5 junctions range.")

    print("Starting simulation tick test...")
    engine.running = True
    
    # Tick through the route
    found_done = False
    for i in range(len(points)):
        engine.tick()
        snap = engine.snapshot()
        
        # Check if any signal became 'done'
        done_signals = [s for s in snap['signals'] if s['state'] == 'done']
        if done_signals and not found_done:
            print(f"Step {i}: Signal {done_signals[0]['id']} is now DONE.")
            found_done = True
            
        if snap['arrived']:
            print(f"Arrived at destination at step {i}.")
            break
            
    print("Final Snapshot Progress:", snap['progress'])
    print("Final Snapshot ETA:", snap['eta'])
    print("Test complete.")

if __name__ == "__main__":
    asyncio.run(test_engine_and_signals())
