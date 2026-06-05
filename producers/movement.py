import math
import random
import time

from core.config import PLAYERS, MAP_SIZE, MAX_STEP, MOVEMENT_DELAY
from core.events import MovementEvent, now_utc

class PlayerPosition:
    def __init__(self, name: str):
        self.name = name
        self.x = random.uniform(0, MAP_SIZE)
        self.y = random.uniform(0, MAP_SIZE)

    def step(self) -> MovementEvent:
        angle = random.uniform(0, 2 * math.pi)
        dist = random.uniform(0, MAX_STEP)
        self.x = max(0.0, min(MAP_SIZE, self.x + dist * math.cos(angle)))
        self.y = max(0.0, min(MAP_SIZE, self.y + dist * math.sin(angle)))
        return MovementEvent(self.name, self.x, self.y, now_utc())
    
def movement_producer(count: int = None, delay: float = MOVEMENT_DELAY):
    positions = {name: PlayerPosition(name) for name in PLAYERS}
    emitted = 0
    while count is None or emitted < count:
        for name in PLAYERS:
            yield positions[name].step()
        emitted += 1
        time.sleep(delay)

if __name__ == "__main__":
    for event in movement_producer(count=2, delay=0.2):
        print(event)
