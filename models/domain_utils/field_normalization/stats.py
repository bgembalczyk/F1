from __future__ import annotations

import contextlib

DRIVER_STATS_HEADER_VARIANTS: tuple[tuple[str, ...], ...] = (
    ("wins", "podiums", "poles"),
    ("wins", "top tens", "poles"),
)


def normalize_stats_headers(headers: list[str]) -> list[str]:
    return [str(header).lower().strip() for header in headers]


def is_driver_stats_table(headers: list[str], *, expected_columns: int) -> bool:
    if len(headers) != expected_columns:
        return False
    return tuple(normalize_stats_headers(headers)) in DRIVER_STATS_HEADER_VARIANTS


def extract_driver_stats_row(row: list[str], headers: list[str]) -> dict[str, int]:
    normalized_headers = normalize_stats_headers(headers)
    stats: dict[str, int | None] = {
        "wins": None,
        "podiums": None,
        "top_tens": None,
        "poles": None,
    }

    with contextlib.suppress(ValueError, IndexError):
        stats["wins"] = int(row[0])

    if "podiums" in normalized_headers:
        with contextlib.suppress(ValueError, IndexError):
            stats["podiums"] = int(row[1])
    elif "top tens" in normalized_headers:
        with contextlib.suppress(ValueError, IndexError):
            stats["top_tens"] = int(row[1])

    with contextlib.suppress(ValueError, IndexError):
        stats["poles"] = int(row[2])

    return {key: value for key, value in stats.items() if value is not None}
