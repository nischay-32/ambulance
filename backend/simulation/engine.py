import asyncio
import time
import sys
import os

# Add parent directory to path so we can import signal_controller
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from signal_controller import SignalController

class SimulationEngine:
    def __init__(self):
        self.running = False
        self.paused = False
        self.current_route = []
        self.current_index = 0
        self.current_position = None
        self.signals = []
        self.sc = SignalController()
        self.start_time = 0
        self.arrived = False
        self.step = 0
        self.time_saved = 4.2 # Mock value for time saved in minutes

    def set_route(self, route_points, steps):
        self.current_route = route_points
        self.current_index = 0
        self.current_position = route_points[0] if route_points else None
        self.signals = self.sc.initialize_signals(route_points, steps)
        self.start_time = time.time()
        self.arrived = False
        self.step = 0
        self.running = True

    def get_signals(self):
        return self.signals

    def tick(self):
        if not self.running or self.paused or self.arrived:
            return

        if self.current_index < len(self.current_route) - 1:
            self.current_index += 1
            self.current_position = self.current_route[self.current_index]
            self.step = self.current_index
            
            # Update signals based on new position
            self.signals = self.sc.update_signals(self.current_position)
            
            if self.current_index == len(self.current_route) - 1:
                self.arrived = True
                self.running = False
        else:
            self.arrived = True
            self.running = False

    def snapshot(self):
        # Calculate progress
        total_pts = len(self.current_route) - 1
        progress = (self.current_index / max(1, total_pts)) * 100 if total_pts > 0 else 100
        
        # Calculate ETA (simplified: each tick is ~0.11s)
        remaining_points = total_pts - self.current_index
        eta = round(remaining_points * 0.11, 1)
        
        return {
            "ambulance_location": self.current_position,
            "point_index": self.current_index,
            "signals": self.signals,
            "running": self.running,
            "paused": self.paused,
            "arrived": self.arrived,
            "step": self.step,
            "progress": round(progress, 1),
            "eta": f"{int(eta // 60)}m {int(eta % 60)}s" if eta > 60 else f"{int(eta)}s",
            "time_saved": f"{self.time_saved} min",
        }

    def pause(self):
        self.paused = not self.paused

    def reset(self):
        self.running = False
        self.paused = False
        self.current_index = 0
        self.current_position = self.current_route[0] if self.current_route else None
        self.arrived = False
        self.step = 0

engine = SimulationEngine()
