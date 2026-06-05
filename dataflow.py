import queue
import threading
import time

import bytewax.operators as op
from bytewax.dataflow import Dataflow
from bytewax.operators.windowing import (
    EventClock, SlidingWindower, TumblingWindower, fold_window,
)

from core.config import (
    PLAYERS, KILL_DELAY, DAMAGE_DELAY, MOVEMENT_DELAY, ALIGN_TO,
    DAMAGE_WINDOW_LENGTH, DAMAGE_WINDOW_OFFSET, MOVEMENT_WINDOW_LENGTH,
    WATERMARK_WAIT,
)
from producers.kill import generate_kill_event
from producers.damage import generate_damage_event
from producers.movement import PlayerPosition
 
from streaming.source import QueueSource
from streaming.sink import ConsoleSink
 
from queries.kda import fan_out_kill, update_kda, format_kda
from queries.damage_board import DamageBoard, format_damage
from queries.distance import DistanceTracker, format_distance

kill_queue: "queue.Queue" = queue.Queue()
damage_queue: "queue.Queue" = queue.Queue()
movement_queue: "queue.Queue" = queue.Queue()

def _run_kill_producer():
    while True:
        kill_queue.put(generate_kill_event())
        time.sleep(KILL_DELAY)

def _run_damage_producer():
    while True:
        damage_queue.put(generate_damage_event())
        time.sleep(DAMAGE_DELAY)

def _run_movement_producer():
    positions = {name: PlayerPosition(name) for name in PLAYERS}
    while True:
        for name in PLAYERS:
            movement_queue.put(positions[name].step())
        time.sleep(MOVEMENT_DELAY)

def start_producers() -> None:
    for target in (_run_kill_producer, _run_damage_producer, _run_movement_producer):
        threading.Thread(target=target, daemon=True).start()

def build_dataflow() -> Dataflow:
    flow = Dataflow("esports")

    kills = op.input("kills_in", flow, QueueSource(kill_queue))
    deltas = op.flat_map("kill_fanout", kills, fan_out_kill)
    keyed_deltas = op.key_on("key_by_player", deltas, lambda pair: pair[0])
    kda = op.stateful_map("kda_state", keyed_deltas, update_kda)
    op.output("kda_out", kda, ConsoleSink(format_kda))

    damage = op.input("dmg_in", flow, QueueSource(damage_queue))
    keyed_damage = op.key_on("dmg_key", damage, lambda _event: "ALL")
    damage_clock = EventClock(
        ts_getter=lambda e: e.timestamp,
        wait_for_system_duration=WATERMARK_WAIT,
    )
    damage_window = SlidingWindower(
        length=DAMAGE_WINDOW_LENGTH,
        offset=DAMAGE_WINDOW_OFFSET,
        align_to=ALIGN_TO,
    )
    damage_folded = fold_window(
        "dmg_window",
        keyed_damage,
        damage_clock,
        damage_window,
        builder=lambda: DamageBoard(),
        folder=lambda board, event: board.add(event),
        merger=lambda a, b: a.merge(b),
    )
    op.output("dmg_out", damage_folded.down, ConsoleSink(format_damage))

    movement = op.input("mov_in", flow, QueueSource(movement_queue))
    keyed_movement = op.key_on("mov_key", movement, lambda e: e.player)
    movement_clock = EventClock(
        ts_getter=lambda e: e.timestamp,
        wait_for_system_duration=WATERMARK_WAIT,
    )
    movement_window = TumblingWindower(
        length=MOVEMENT_WINDOW_LENGTH,
        align_to=ALIGN_TO,
    )
    distance_folded = fold_window(
        "mov_window",
        keyed_movement,
        movement_clock,
        movement_window,
        builder=lambda: DistanceTracker(),
        folder=lambda tracker, event: tracker.add(event),
        merger=lambda a, b: a.merge(b),
    )
    op.output("mov_out", distance_folded.down, ConsoleSink(format_distance))
 
    return flow

start_producers()
flow = build_dataflow()

if __name__ == "__main__":
    from bytewax.run import cli_main
 
    print("Esports stream processing (Bytewax)")
    print("Players:", ", ".join(PLAYERS))
    print("Q1 KDA (per-player state) | Q2 damage (30s sliding) | Q3 distance (20s tumbling)")
    print("-" * 70)
    cli_main(flow)
