import re
from typing import Any

from models.services.season_service import parse_seasons
from models.value_objects.drivers_championships import DriversChampionships
from models.value_objects.season_ref import SeasonRef


def _extract_count(text: str) -> tuple[int, list[str]]:
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    if not lines:
        return 0, []

    match = re.match(r"(\d+)", lines[0])
    if match:
        count = int(match.group(1))
        tail = lines[0][match.end() :].strip()
        parts: list[str] = []
        if tail:
            parts.append(tail)
        parts.extend(lines[1:])
        return count, parts

    fallback = re.search(r"\d+", text)
    count = int(fallback.group(0)) if fallback else 0
    parts = lines[1:] if len(lines) > 1 else []
    return count, parts


def _parse_season_parts(parts: list[str]) -> list[SeasonRef]:
    if not parts:
        return []
    seasons_text = ", ".join(parts)
    return parse_seasons(seasons_text)


def parse_championships(raw: Any) -> DriversChampionships:
    """
    Parsuje tekst z komórki "Drivers' Championships" do postaci:

        DriversChampionships(count=<int>, seasons=[SeasonRef(...), ...])

    Przykładowe wejście (raw, po bazowym parsowaniu typu "text"):
    - "0"
    - "2\n2005-2006"
    - "7\n1994-1995, 2000-2004"
    """
    text = str(raw) if raw is not None else ""
    text = text.replace("\r\n", "\n").replace("\r", "\n").strip()
    if not text:
        return DriversChampionships()

    count, seasons_parts = _extract_count(text)
    seasons = [] if count == 0 else _parse_season_parts(seasons_parts)

    return DriversChampionships(count=count, seasons=seasons)
