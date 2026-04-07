from pathlib import Path
from typing import Any

from validation.validator_base import ExportRecord


def fieldnames_from_union(data: list[ExportRecord]) -> list[str]:
    keys: list[str] = []
    for row in data:
        for key in row:
            if key not in keys:
                keys.append(key)
    return keys


def fieldnames_from_first_row(data: list[ExportRecord]) -> list[str]:
    return list(data[0].keys()) if data else []
