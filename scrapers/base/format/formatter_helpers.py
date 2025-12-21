from __future__ import annotations

from dataclasses import asdict, is_dataclass
from typing import Any, Dict, List, cast

from models.records import LinkRecord

from models.mappers.serialization import to_dict_list
from scrapers.base.results import ScrapeResult


def _normalize_payload(value: Any) -> Any:
    """
    Fallback normalizacji do struktur JSON-serializowalnych.

    Zasada:
    - najpierw próbujemy oficjalnej ścieżki (to_dict_list w _extract_data),
      a to jest tylko "plan B" na pojedyncze wartości w meta/data.
    """
    if hasattr(value, "to_dict") and callable(value.to_dict):
        return _normalize_payload(value.to_dict())
    if hasattr(value, "model_dump") and callable(value.model_dump):
        return _normalize_payload(value.model_dump())
    if hasattr(value, "dict") and callable(value.dict):
        return _normalize_payload(value.dict())
    if is_dataclass(value):
        return _normalize_payload(asdict(value))
    if isinstance(value, dict):
        if "text" in value and "url" in value and set(value.keys()).issubset(
            {"text", "url"}
        ):
            return cast(
                LinkRecord,
                {"text": value.get("text") or "", "url": value.get("url")},
            )
        return {k: _normalize_payload(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_normalize_payload(v) for v in value]
    if isinstance(value, tuple):
        return tuple(_normalize_payload(v) for v in value)
    return value


def _extract_data(result: ScrapeResult) -> List[Dict[str, Any]]:
    """
    Główna, spójna ścieżka ekstrakcji danych:
    - zawsze zwracamy list[dict[str,Any]]
    - wykorzystujemy to_dict_list (Twoja wspólna warstwa serializacji)
    """
    data = result.data

    try:
        return to_dict_list(list(data))
    except TypeError:
        normalized = _normalize_payload(list(data))
        if isinstance(normalized, list):
            out: List[Dict[str, Any]] = []
            for item in normalized:
                if isinstance(item, dict):
                    out.append(item)
                else:
                    out.append({"value": item})
            return out
        return [{"value": normalized}]
