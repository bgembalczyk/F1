from typing import Iterable


def expand_range(start: int, end: int) -> Iterable[int]:
    if end < start:
        start, end = end, start
    return range(start, end + 1)


def expand_all(total_rounds: int | None) -> list[int]:
    if total_rounds is None or total_rounds <= 0:
        return []
    return list(range(1, total_rounds + 1))


def unique_sorted(values: Iterable[int]) -> list[int]:
    seen = set(values)
    return sorted(seen)
