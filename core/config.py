from datetime import datetime, timezone, timedelta

PLAYERS = [ "Arthas", "Thrall", "Jaina", "Sylvanas", "Illidan", "Malfurion", "Garrosh", "Varian" ]

ABILITIES = {
    "Arthas":    ["Frostmourne Strike", "Death Coil", "Howling Blast"],
    "Thrall":    ["Chain Lightning", "Earthquake", "Feral Spirit"],
    "Jaina":     ["Frostbolt", "Blizzard", "Ice Lance"],
    "Sylvanas":  ["Black Arrow", "Withering Fire", "Shadow Trap"],
    "Illidan":   ["Blade Dance", "Metamorphosis", "Eye Beam"],
    "Malfurion": ["Moonfire", "Starfall", "Entangling Roots"],
    "Garrosh":   ["Mortal Strike", "Whirlwind", "Heroic Leap"],
    "Varian":    ["Heroic Strike", "Colossus Smash", "Execute"]
}

DAMAGE_RANGES = {
    "Arthas":    (300, 900),
    "Thrall":    (250, 800),
    "Jaina":     (400, 1200),
    "Sylvanas":  (200, 700),
    "Illidan":   (350, 950),
    "Malfurion": (150, 600),
    "Garrosh":   (400, 1100),
    "Varian":    (350, 1000)
}

MAP_SIZE = 1000.0
MAX_STEP = 30.0

KILL_DELAY = 1.5
DAMAGE_DELAY = 0.4
MOVEMENT_DELAY = 0.3

ALIGN_TO = datetime(2026, 1, 1, tzinfo=timezone.utc)

DAMAGE_WINDOW_LENGTH = timedelta(seconds=30)
DAMAGE_WINDOW_OFFSET = timedelta(seconds=10)

MOVEMENT_WINDOW_LENGTH = timedelta(seconds=20)

WATERMARK_WAIT = timedelta(seconds=5)
