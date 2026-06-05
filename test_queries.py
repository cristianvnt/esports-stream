from datetime import datetime, timezone

from core.events import KillEvent, DamageEvent, MovementEvent
from queries.kda import fan_out_kill, KDAState, StatDelta, update_kda
from queries.damage_board import DamageBoard
from queries.distance import DistanceTracker

TS = datetime(2026, 1, 1, tzinfo=timezone.utc)


# Query 1: KDA
def test_fan_out_kill_no_assists():
    # One kill, no assists
    ev = KillEvent("Arthas", "Thrall", [], TS)
    records = fan_out_kill(ev)
    assert records == [("Arthas", StatDelta(kills=1)), ("Thrall", StatDelta(deaths=1))]


def test_fan_out_kill_with_assists():
    # Two assists
    ev = KillEvent("Arthas", "Thrall", ["Jaina", "Varian"], TS)
    records = fan_out_kill(ev)
    assert len(records) == 4
    assert ("Jaina", StatDelta(assists=1)) in records
    assert ("Varian", StatDelta(assists=1)) in records


def test_kda_ratio_formula():
    # (kills + assists/2) / max(deaths, 1)
    s = KDAState()
    s.apply(StatDelta(kills=2))
    s.apply(StatDelta(deaths=2))
    s.apply(StatDelta(assists=1))
    # (2 + 0.5) / 2 = 1.25
    assert s.ratio() == 1.25


def test_kda_ratio_zero_deaths_no_crash():
    s = KDAState()
    s.apply(StatDelta(kills=3))
    assert s.ratio() == 3.0


def test_update_kda_threads_state():
    state = None
    state, out = update_kda(state, ("Arthas", StatDelta(kills=1)))
    state, out = update_kda(state, ("Arthas", StatDelta(kills=1)))
    state, out = update_kda(state, ("Arthas", StatDelta(deaths=1)))
    assert out == ("Arthas", 2, 1, 0, 2.0)  # (2 + 0)/1 = 2.0


# Query 2: DamageBoard
def test_damage_board_accumulates():
    b = DamageBoard()
    b.add(DamageEvent("Jaina", "Arthas", 100, "Frostbolt", TS))
    b.add(DamageEvent("Jaina", "Thrall", 50, "Blizzard", TS))
    b.add(DamageEvent("Arthas", "Jaina", 70, "Death Coil", TS))
    assert b.totals == {"Jaina": 150, "Arthas": 70}


def test_damage_ranking_descending():
    b = DamageBoard()
    b.add(DamageEvent("Jaina", "X", 100, "a", TS))
    b.add(DamageEvent("Arthas", "X", 300, "a", TS))
    b.add(DamageEvent("Thrall", "X", 200, "a", TS))
    ranking = b.ranking()
    assert ranking == [("Arthas", 300), ("Thrall", 200), ("Jaina", 100)]


def test_damage_merge_is_additive():
    a = DamageBoard()
    a.add(DamageEvent("Jaina", "X", 100, "ab", TS))
    b = DamageBoard()
    b.add(DamageEvent("Jaina", "X", 50, "ab", TS))
    b.add(DamageEvent("Arthas", "X", 80, "ab", TS))
    merged = a.merge(b)
    assert merged.totals == {"Jaina": 150, "Arthas": 80}
    assert a.totals == {"Jaina": 100}


# Query 3: DistanceTracker
def test_distance_pythagoras():
    # (0,0) -> (3,4) is a classic 3-4-5 triangle: distance 5.
    t = DistanceTracker()
    t.add(MovementEvent("Arthas", 0.0, 0.0, TS))
    t.add(MovementEvent("Arthas", 3.0, 4.0, TS))
    assert t.total == 5.0


def test_distance_first_event_is_zero():
    # A single position has no previous point -> no distance yet.
    t = DistanceTracker()
    t.add(MovementEvent("Arthas", 10.0, 10.0, TS))
    assert t.total == 0.0


def test_distance_accumulates_multiple_steps():
    # (0,0)->(0,3)=3, then (0,3)->(4,3)=4, total 7.
    t = DistanceTracker()
    t.add(MovementEvent("Arthas", 0.0, 0.0, TS))
    t.add(MovementEvent("Arthas", 0.0, 3.0, TS))
    t.add(MovementEvent("Arthas", 4.0, 3.0, TS))
    assert t.total == 7.0


def test_distance_merge_sums_totals():
    a = DistanceTracker(); a.total = 10.0; a.last_x, a.last_y = 5.0, 5.0
    b = DistanceTracker(); b.total = 7.0;  b.last_x, b.last_y = 9.0, 9.0
    merged = a.merge(b)
    assert merged.total == 17.0


if __name__ == "__main__":
    import sys
    funcs = [v for k, v in sorted(globals().items()) if k.startswith("test_") and callable(v)]
    passed = 0
    for fn in funcs:
        try:
            fn()
            print(f"PASS  {fn.__name__}")
            passed += 1
        except AssertionError as e:
            print(f"FAIL  {fn.__name__}  -> {e!r}")
        except Exception as e:
            print(f"ERROR {fn.__name__}  -> {type(e).__name__}: {e}")
    print(f"\n{passed}/{len(funcs)} passed")
    sys.exit(0 if passed == len(funcs) else 1)