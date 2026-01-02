import re
from dataclasses import dataclass
from typing import Iterable


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
            return _expand_all(total_rounds)

        normalized = re.sub(r"\b(rounds?|races?)\b", "", normalized, flags=re.I)
        parts = [p.strip() for p in re.split(r"[;,]", normalized) if p.strip()]

        values: list[int] = []
        for part in parts:
            if not part:
                continue

            if "all" in part.lower():
                values.extend(_expand_all(total_rounds))
                continue

            match = re.match(r"^(\d+)\s*[\u2013\u2014-]\s*(\d+)$", part)
            if match:
                start = int(match.group(1))
                end = int(match.group(2))
                values.extend(_expand_range(start, end))
                continue

            match = re.search(r"\d+", part)
            if match:
                values.append(int(match.group(0)))

        return _unique_sorted(values)


def _expand_range(start: int, end: int) -> Iterable[int]:
    if end < start:
        start, end = end, start
    return range(start, end + 1)


def _expand_all(total_rounds: int | None) -> list[int]:
    if total_rounds is None or total_rounds <= 0:
        return []
    return list(range(1, total_rounds + 1))


def _unique_sorted(values: Iterable[int]) -> list[int]:
    seen = set(values)
    return sorted(seen)
