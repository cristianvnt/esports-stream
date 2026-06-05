from dataclasses import dataclass, field
from typing import Dict, List, Tuple

from core.events import DamageEvent

@dataclass
class DamageBoard:
    totals: Dict[str, int] = field(default_factory=dict)

    def add(self, event: DamageEvent) -> "DamageBoard":
        self.totals[event.attacker] = self.totals.get(event.attacker, 0) + event.damage_amount
        return self
    
    def merge(self, other: "DamageBoard") -> "DamageBoard":
        out = DamageBoard(dict(self.totals))
        for player, dmg in other.totals.items():
            out.totals[player] = out.totals.get(player, 0) + dmg
        return out
    
    def ranking(self, top_n: int = 3) -> List[Tuple[str, int]]:
        return sorted(self.totals.items(), key=lambda kv: kv[1], reverse=True)[:top_n]
    
def format_damage(item) -> str:
    _, (_, board) = item
    ranking = board.ranking()
    if not ranking:
        return "[DMG 30s] (no damage yet)"
    leader, leader_dmg = ranking[0]
    rest = "  ".join(f"{p}:{d}" for p, d in ranking[1:])
    line = f"[DMG 30s] TOP: {leader} ({leader_dmg})"
    if rest:
        line += f"   | {rest}"
    return line
