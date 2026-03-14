import re
from dataclasses import dataclass

from models.services.helpers import expand_all
from models.services.helpers import expand_range
from models.services.helpers import unique_sorted


@dataclass(frozen=True)
class RoundsService:
    @staticmethod
    def parse_rounds(text: str | None, *, total_rounds: int | None = None) -> list[int]:
        if not text:
            return []

        normalized = text.strip()
        if not normalized:
            return []

        lower = normalized.lower()
        if "all" in lower:
            return expand_all(total_rounds)

        normalized = re.sub(
            r"\b(rounds?|races?)\b",
            "",
            normalized,
            flags=re.IGNORECASE,
        )
        parts = [p.strip() for p in re.split(r"[;,]", normalized) if p.strip()]

        values: list[int] = []
        for part in parts:
            if not part:
                continue

            if "all" in part.lower():
                values.extend(expand_all(total_rounds))
                continue

            match = re.match(r"^(\d+)\s*[\u2013\u2014-]\s*(\d+)$", part)
            if match:
                start = int(match.group(1))
                end = int(match.group(2))
                values.extend(expand_range(start, end))
                continue

            match = re.search(r"\d+", part)
            if match:
                values.append(int(match.group(0)))

        return unique_sorted(values)
