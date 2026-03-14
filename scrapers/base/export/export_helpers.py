from typing import Any

from scrapers.base.results import ScrapeResult
from validation.validator_base import ExportRecord


def extract_data(result: ScrapeResult) -> list[Any]:
    # Lekka lokalna stubs - import typu w czasie wykonania,
    # żeby uniknąć cyklicznych importów
    if isinstance(result, ScrapeResult):
        return list(result.data)
    msg = "Expected ScrapeResult."
    raise TypeError(msg)


def fieldnames_from_union(data: list[ExportRecord]) -> list[str]:
    keys: list[str] = []
    for row in data:
        for key in row:
            if key not in keys:
                keys.append(key)
    return keys


def fieldnames_from_first_row(data: list[ExportRecord]) -> list[str]:
    return list(data[0].keys()) if data else []
