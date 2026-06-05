from dataclasses import dataclass
from typing import List, Tuple

from core.events import KillEvent

@dataclass
class StatDelta:
    kills: int = 0
    deaths: int = 0
    assists: int = 0

def fan_out_kill(event: KillEvent) -> List[Tuple[str, StatDelta]]:
    records: List[Tuple[str, StatDelta]] = [
        (event.killer, StatDelta(kills=1)),
        (event.victim, StatDelta(deaths=1)),
    ]
    for assistant in event.assistants:
        records.append((assistant, StatDelta(assists=1)))
    return records

@dataclass
class KDAState:
    kills: int = 0
    deaths: int = 0
    assists: int = 0

    def apply(self, delta: StatDelta) -> None:
        self.kills += delta.kills
        self.deaths += delta.deaths
        self.assists += delta.assists

    def ratio(self) -> float:
        return round((self.kills + self.assists / 2) / max(self.deaths, 1), 2)
    
def update_kda(state, value: Tuple[str, StatDelta]):
    player, delta = value
    if state is None:
        state = KDAState()
    state.apply(delta)
    snapshot = (player, state.kills, state.deaths, state.assists, state.ratio())
    return state, snapshot

def format_kda(item) -> str:
    _, (player, k, d, a, ratio) = item
    return f"[KDA] {player:10s} K={k} D={d} A={a}  ratio={ratio}"
