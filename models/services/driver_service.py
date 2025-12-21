from __future__ import annotations

from dataclasses import dataclass
import re
from typing import Any

from models.services.season_service import SeasonService


@dataclass(frozen=True)
class DriverService:
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
        - "2\n2005–2006"
        - "7\n1994–1995, 2000–2004"
        """
        text = (str(raw) if raw is not None else "").strip()
        if not text:
            return {"count": 0, "seasons": []}

        lines = [ln.strip() for ln in text.splitlines() if ln.strip()]

        count = 0
        seasons_parts: list[str] = []

        if lines:
            # pierwsza linia zwykle zaczyna się od liczby tytułów
            m = re.match(r"(\d+)", lines[0])
            if m:
                count = int(m.group(1))
                tail = lines[0][m.end():].strip()
                if tail:
                    seasons_parts.append(tail)
                # reszta linii traktujemy jako kolejne fragmenty z latami
                seasons_parts.extend(lines[1:])
            else:
                # fallback – spróbuj wyciągnąć liczbę z całego tekstu
                m2 = re.search(r"\d+", text)
                if m2:
                    count = int(m2.group(1))
                seasons_parts = lines[1:] if len(lines) > 1 else []
        else:
            # gdyby coś poszło nie tak z lines
            m2 = re.search(r"\d+", text)
            if m2:
                count = int(m2.group(1))

        # jeśli count == 0 albo nie ma fragmentu z latami – nie ma sezonów
        if count == 0 or not seasons_parts:
            return {"count": count, "seasons": []}

        seasons_text = ", ".join(seasons_parts)
        seasons = SeasonService.parse_seasons(seasons_text)

        return {"count": count, "seasons": seasons}
