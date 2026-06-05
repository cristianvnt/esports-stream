from dataclasses import dataclass
from datetime import datetime, timezone
from typing import List

def now_utc() -> datetime:
    return datetime.now(timezone.utc)

@dataclass
class KillEvent:
    killer: str
    victim: str
    assistants: List[str]
    timestamp: datetime

    def __repr__(self) -> str:
        assists = ", ".join(self.assistants) if self.assistants else "none"
        return f"[KILL] {self.killer} -> {self.victim} (assists: {assists}) @ {self.timestamp:%H:%M:%S}"
    
@dataclass
class DamageEvent:
    attacker: str
    target: str
    damage_amount: int
    ability: str
    timestamp: datetime

    def __repr__(self) -> str:
        return f"[DMG] {self.attacker} -> {self.target} ({self.ability}, {self.damage_amount}) @ {self.timestamp:%H:%M:%S}"
    
@dataclass
class MovementEvent:
    player: str
    x: float
    y: float
    timestamp: datetime

    def __repr__(self) -> str:
        return f"[MOV] {self.player} -> ({self.x:.1f}, {self.y:.1f}) @ {self.timestamp:%H:%M:%S}"
