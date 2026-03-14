import re
from dataclasses import dataclass
from datetime import datetime
from datetime import timezone
from typing import Any

RANGE_PATTERN = re.compile(r"(\d{4})\s*[\u2013-]\s*(\d{4})")
RANGE_TO_PATTERN = re.compile(r"(\d{4})\s+to\s+(\d{4})", re.IGNORECASE)
SINGLE_YEAR_PATTERN = re.compile(r"\d{4}")


@dataclass(frozen=True)
class SeasonService:
    @staticmethod
    def _normalize_text(text: str, current_year: int) -> str:
        """Normalize season text by replacing onward(s) and present with a year."""
        text = re.sub(
            r"(\d{4})\s+onward(?:s)?\b",
            r"\1-present",
            text,
            flags=re.IGNORECASE,
        )
        return re.sub(r"\bpresent\b", str(current_year), text, flags=re.IGNORECASE)

    @staticmethod
    def _extract_years_from_part(part: str) -> list[int]:
        range_match = RANGE_PATTERN.fullmatch(part)
        if range_match:
            start = int(range_match.group(1))
            end = int(range_match.group(2))
            if end < start:
                start, end = end, start
            return list(range(start, end + 1))

        range_to_match = RANGE_TO_PATTERN.fullmatch(part)
        if range_to_match:
            start = int(range_to_match.group(1))
            end = int(range_to_match.group(2))
            if end < start:
                start, end = end, start
            return list(range(start, end + 1))

        return [int(part)] if SINGLE_YEAR_PATTERN.fullmatch(part) else []

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

        normalized_text = SeasonService._normalize_text(text, current_year)
        parts = [p.strip() for p in normalized_text.split(",") if p.strip()]

        result: list[dict[str, Any]] = []
        seen: set[int] = set()

        for part in parts:
            for year in SeasonService._extract_years_from_part(part):
                if year in seen:
                    continue
                seen.add(year)
                result.append(
                    {
                        "year": year,
                        "url": (
                            "https://en.wikipedia.org/wiki/"
                            f"{year}_Formula_One_World_Championship"
                        ),
                    },
                )

        return result
