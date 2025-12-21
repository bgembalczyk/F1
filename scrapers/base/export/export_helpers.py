from __future__ import annotations

import re
from typing import Any, Callable, Dict, List, TypeAlias

# Nie wiążemy się twardo z "scrapers.base.types.ExportableRecord",
# bo w Twoich branchach to nie jest stabilne API.
ExportRecord: TypeAlias = Dict[str, Any]
NormalizationRule = Callable[[Dict[str, Any]], Dict[str, Any]]


def _extract_data(result: "ScrapeResult | List[Any]") -> List[Any]:
    # Lekka lokalna stubs — import typu w czasie wykonania, żeby uniknąć cyklicznych importów
    from scrapers.base.results import ScrapeResult

    if isinstance(result, ScrapeResult):
        return list(result.data)
    return list(result)


def _normalize_record_keys(record: Dict[str, Any]) -> Dict[str, Any]:
    normalized: Dict[str, Any] = {}
    for key, value in record.items():
        normalized_key = _to_snake_case(str(key))
        if not normalized_key:
            continue
        normalized[normalized_key] = value
    return normalized


def _drop_empty_fields(record: Dict[str, Any]) -> Dict[str, Any]:
    return {key: value for key, value in record.items() if not _is_empty(value)}


def _is_empty(value: Any) -> bool:
    if value is None:
        return True
    if isinstance(value, str):
        return value.strip() == ""
    if isinstance(value, (list, tuple, set, dict)):
        return len(value) == 0
    return False


def _to_snake_case(value: str) -> str:
    cleaned = re.sub(r"[^0-9a-zA-Z]+", "_", value)
    cleaned = re.sub(r"_+", "_", cleaned).strip("_")
    return cleaned.lower()


def _fieldnames_from_union(data: List[ExportRecord]) -> List[str]:
    keys: List[str] = []
    for row in data:
        for key in row.keys():
            if key not in keys:
                keys.append(key)
    return keys


def _fieldnames_from_first_row(data: List[ExportRecord]) -> List[str]:
    return list(data[0].keys()) if data else []
