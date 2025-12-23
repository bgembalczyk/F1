from dataclasses import dataclass
from datetime import datetime
import re
from typing import Any


@dataclass(frozen=True)
class SeasonService:
    @staticmethod
    def parse_seasons(
        text: str, *, current_year: int | None = None
    ) -> list[dict[str, Any]]:
        """
        Zamienia tekst w stylu:
            '1973, 1975–1982, 1984'  lub '2014–present'
        na listę:
            [{"year": 1973, "url": ...}, {"year": 1975, "url": ...}, ..., {"year": 1984, "url": ...}]

        'present' (case-insensitive) → aktualny rok.
        """
        result: list[dict[str, Any]] = []
        seen: set[int] = set()

        if not text:
            return result

        if current_year is None:
            current_year = datetime.now().year

        # Zamień 'present' na aktualny rok (case-insensitive)
        text = re.sub(r"\bpresent\b", str(current_year), text, flags=re.IGNORECASE)

        parts = [p.strip() for p in text.split(",") if p.strip()]

        for part in parts:
            # zakres: 1975–1982 (en dash lub zwykły minus)
            m_range = re.fullmatch(r"(\d{4})\s*[\u2013-]\s*(\d{4})", part)
            if m_range:
                start = int(m_range.group(1))
                end = int(m_range.group(2))
                if end < start:
                    start, end = end, start
                years = range(start, end + 1)
            else:
                # pojedynczy rok: 1973
                m_year = re.fullmatch(r"\d{4}", part)
                if not m_year:
                    continue
                years = [int(part)]

            for y in years:
                if y in seen:
                    continue
                seen.add(y)
                url = (
                    f"https://en.wikipedia.org/wiki/{y}_Formula_One_World_Championship"
                )
                result.append({"year": y, "url": url})

        return result
