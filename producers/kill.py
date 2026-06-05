import random
import time

from core.config import PLAYERS, KILL_DELAY
from core.events import KillEvent, now_utc

def generate_kill_event() -> KillEvent:
    killer = random.choice(PLAYERS)
    pool = [p for p in PLAYERS if p != killer]
    victim = random.choice(pool)
    pool = [p for p in pool if p != victim]
    assistants = random.sample(pool, random.randint(0, 2))

    return KillEvent(killer, victim, assistants, now_utc())

def kill_producer(count: int = None, delay: float = KILL_DELAY):
    emitted = 0
    while count is None or emitted < count:
        yield generate_kill_event()
        emitted += 1
        time.sleep(delay)

if __name__ == "__main__":
    for event in kill_producer(count=5, delay=0.2):
        print(event)
