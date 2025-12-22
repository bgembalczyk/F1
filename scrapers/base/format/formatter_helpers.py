from __future__ import annotations

from typing import Any, Dict, List

from models.mappers.serialization import to_dict_list
from models.serializers import to_dict_any
from scrapers.base.results import ScrapeResult


def extract_data(result: ScrapeResult) -> List[Dict[str, Any]]:
    """
    Główna, spójna ścieżka ekstrakcji danych:
    - zawsze zwracamy list[dict[str,Any]]
    - wykorzystujemy to_dict_list (Twoja wspólna warstwa serializacji)
    """
    data = result.data

    try:
        return to_dict_list(list(data))
    except TypeError:
        normalized = to_dict_any(list(data))
        if isinstance(normalized, list):
            out: List[Dict[str, Any]] = []
            for item in normalized:
                if isinstance(item, dict):
                    out.append(item)
                else:
                    out.append({"value": item})
            return out
        return [{"value": normalized}]
