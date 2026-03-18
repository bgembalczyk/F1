"""Domain helpers for Formula One season Wikipedia URLs."""

from __future__ import annotations

import re

WIKIPEDIA_BASE_URL = "https://en.wikipedia.org"
WIKIPEDIA_WIKI_PATH = "/wiki"
FORMULA_ONE_SEASONS_LIST_URL = (
    f"{WIKIPEDIA_BASE_URL}{WIKIPEDIA_WIKI_PATH}/List_of_Formula_One_seasons"
)
FORMULA_ONE_SEASON_URL_TEMPLATE = (
    f"{WIKIPEDIA_BASE_URL}{WIKIPEDIA_WIKI_PATH}/{{year}}_Formula_One_World_Championship"
)

_SEASON_YEAR_IN_URL_PATTERN = re.compile(r"(?:^|/)(?P<year>\d{4})_Formula_One(?:_|$)")


def build_season_url(year: int) -> str:
    """Build the canonical Wikipedia URL for a Formula One World Championship season."""
    return FORMULA_ONE_SEASON_URL_TEMPLATE.format(year=year)


def extract_season_year_from_url(url: str) -> int | None:
    """Extract the season year from a season-like Formula One Wikipedia URL."""
    match = _SEASON_YEAR_IN_URL_PATTERN.search(url)
    if match is None:
        return None
    return int(match.group("year"))
