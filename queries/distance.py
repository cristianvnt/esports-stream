import math
from dataclasses import dataclass

from core.events import MovementEvent

@dataclass
class DistanceTracker:
    last_x: float = None
    last_y: float = None
    total: float = 0.0

    def add(self, event: MovementEvent) -> "DistanceTracker":
        if self.last_x is not None:
            dx = event.x - self.last_x
            dy = event.y - self.last_y
            self.total += math.sqrt(dx * dx + dy * dy)
        self.last_x = event.x
        self.last_y = event.y
        return self
    
    def merge(self, other: "DistanceTracker") -> "DistanceTracker":
        out = DistanceTracker()
        out.total = self.total + other.total
        if other.last_x is not None:
            out.last_x, out.last_y = other.last_x, other.last_y
        else:
            out.last_x, out.last_y = self.last_x, self.last_y
        return out
    
def format_distance(item) -> str:
    player, (_, tracker) = item
    return f"[DIST 20s] {player:10s} moved {tracker.total:.1f} units"
