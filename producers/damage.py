import random
import time

from core.config import PLAYERS, ABILITIES, DAMAGE_RANGES, DAMAGE_DELAY
from core.events import DamageEvent, now_utc

def generate_damage_event() -> DamageEvent:
    attacker = random.choice(PLAYERS)
    target = random.choice([p for p in PLAYERS if p != attacker])
    ability = random.choice(ABILITIES[attacker])
    low, high = DAMAGE_RANGES[attacker]
    damage = random.randint(low, high)

    return DamageEvent(attacker, target, damage, ability, now_utc())

def damage_producer(count: int = None, delay: float = DAMAGE_DELAY):
    emitted = 0
    while count is None or emitted < count:
        yield generate_damage_event()
        emitted += 1
        time.sleep(delay)

if __name__ == "__main__":
    for event in damage_producer(count=5, delay=0.2):
        print(event)
