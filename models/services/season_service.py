from dataclasses import dataclass
from datetime import datetime
from datetime import timezone
from typing import Any

from models.domain_utils.years import extract_years


@dataclass(frozen=True)
class SeasonService:
    @staticmethod
    def parse_seasons(
        text: str,
        *,
        current_year: int | None = None,
    ) -> list[dict[str, Any]]:
        """
        Zamienia tekst w stylu:
            '1973, 1975-1982, 1984' lub '2014-present'
        na listę:
            [{"year": 1973, "url": ...}, {"year": 1975, "url": ...}, ...]

        'present' (case-insensitive) -> aktualny rok.
        """
        if not text:
            return []

        if current_year is None:
            current_year = datetime.now(timezone.utc).year

        years = extract_years(text, current_year=current_year)
        return [
            {
                "year": year,
                "url": (
                    "https://en.wikipedia.org/wiki/"
                    f"{year}_Formula_One_World_Championship"
                ),
            }
            for year in years
        ]
