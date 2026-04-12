import re

from scrapers.constants.constants_points import HISTORICAL_POSITIONS
from scrapers.constants.constants_points import SPRINT_POSITIONS

HISTORY_POSITION_KEYS_WITH_FASTEST_LAP: frozenset[str] = frozenset(
    pos.lower() for pos in HISTORICAL_POSITIONS[1:]
) | {"fastest_lap"}



SPRINT_DISQUALIFYING_HEADERS: frozenset[str] = frozenset(
    re.sub(r"[^a-z0-9]+", "", h.lower())
    for h in ("9th", "10th", "Fastest lap", "Race length completed")
)

SPRINT_POSITION_KEYS: frozenset[str] = frozenset(
    pos.lower() for pos in SPRINT_POSITIONS
)
