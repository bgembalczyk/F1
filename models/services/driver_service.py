import re
from dataclasses import dataclass
from typing import Any

from models.services.season_service import SeasonService


@dataclass(frozen=True)
class DriverService:
    @staticmethod
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

    @staticmethod
    def _parse_season_parts(parts: list[str]) -> list[dict[str, Any]]:
        if not parts:
            return []
        seasons_text = ", ".join(parts)
        return SeasonService.parse_seasons(seasons_text)

    @staticmethod
    def parse_championships(raw: Any) -> dict[str, Any]:
        """
        Parsuje tekst z komórki "Drivers' Championships" do postaci:

            {
                "count": <int>,              # liczba tytułów
                "seasons": [ {year, url}, ... ]  # sezony zdobycia tytułu
            }

        Przykładowe wejście (raw, po bazowym parsowaniu typu "text"):
        - "0"
        - "2\n2005-2006"
        - "7\n1994-1995, 2000-2004"
        """
        text = str(raw) if raw is not None else ""
        text = text.replace("\r\n", "\n").replace("\r", "\n").strip()
        if not text:
            return {"count": 0, "seasons": []}

        count, seasons_parts = DriverService._extract_count(text)
        seasons = [] if count == 0 else DriverService._parse_season_parts(seasons_parts)

        return {"count": count, "seasons": seasons}
