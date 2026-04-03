"""Shared table headers and aliases reused across scraper domains."""

from __future__ import annotations

POINTS_HEADER = "Points"
POINTS_ALIASES = ("Pts", "Pts.")

WINS_HEADER = "Wins"
POLES_HEADER = "Poles"
PODIUMS_HEADER = "Podiums"
FASTEST_LAPS_HEADER = "FL"

POINTS_HEADER_TO_KEY = {
    POINTS_HEADER: "points",
    **dict.fromkeys(POINTS_ALIASES, "points"),
}

BASE_METRIC_HEADERS_TO_KEYS = {
    WINS_HEADER: "wins",
    POINTS_HEADER: "points",
    POLES_HEADER: "poles",
    FASTEST_LAPS_HEADER: "fastest_laps",
    PODIUMS_HEADER: "podiums",
}
