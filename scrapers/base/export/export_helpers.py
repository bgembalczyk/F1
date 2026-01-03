from typing import Any, List

from scrapers.base.results import ScrapeResult
from validation.records import ExportRecord


def extract_data(result: ScrapeResult) -> List[Any]:
    # Lekka lokalna stubs — import typu w czasie wykonania, żeby uniknąć cyklicznych importów
    from scrapers.base.results import ScrapeResult

    if isinstance(result, ScrapeResult):
        return list(result.data)
    raise TypeError("Expected ScrapeResult.")


def fieldnames_from_union(data: List[ExportRecord]) -> List[str]:
    keys: List[str] = []
    for row in data:
        for key in row.keys():
            if key not in keys:
                keys.append(key)
    return keys


def fieldnames_from_first_row(data: List[ExportRecord]) -> List[str]:
    return list(data[0].keys()) if data else []
