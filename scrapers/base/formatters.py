from __future__ import annotations

import csv
import importlib.util
import io
import json
import warnings
from dataclasses import asdict, is_dataclass
from typing import Any, Dict, List, Optional, Sequence

from models.mappers.serialization import to_dict_list
from scrapers.base.results import ScrapeResult

_HAS_PANDAS = importlib.util.find_spec("pandas") is not None
if _HAS_PANDAS:
    import pandas as pd


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
        return {k: _normalize_payload(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_normalize_payload(v) for v in value]
    if isinstance(value, tuple):
        return tuple(_normalize_payload(v) for v in value)
    return value


def _extract_data(result: ScrapeResult | List[Any]) -> List[Dict[str, Any]]:
    """
    Główna, spójna ścieżka ekstrakcji danych:
    - zawsze zwracamy list[dict[str,Any]]
    - wykorzystujemy to_dict_list (Twoja wspólna warstwa serializacji)
    """
    data = result.data if isinstance(result, ScrapeResult) else result

    # to_dict_list już obsługuje: Mapping, pydantic (.model_dump/.dict), dataclass itd.
    try:
        return to_dict_list(list(data))
    except TypeError:
        # ultra-fallback: jeśli trafi się coś dziwnego, spróbujmy znormalizować ręcznie
        normalized = _normalize_payload(list(data))
        # po normalizacji nadal chcemy dict-y
        if isinstance(normalized, list):
            out: List[Dict[str, Any]] = []
            for item in normalized:
                if isinstance(item, dict):
                    out.append(item)
                else:
                    out.append({"value": item})
            return out
        return [{"value": normalized}]


class JsonFormatter:
    def format(
        self,
        result: ScrapeResult | List[Any],
        *,
        indent: int = 2,
        include_metadata: bool = False,
    ) -> str:
        payload = self._json_payload(result, include_metadata=include_metadata)
        return json.dumps(payload, ensure_ascii=False, indent=indent)

    def _json_payload(
        self,
        result: ScrapeResult | List[Any],
        *,
        include_metadata: bool,
    ) -> Any:
        if not include_metadata:
            return _extract_data(result)

        if isinstance(result, ScrapeResult):
            return {
                "meta": {
                    "source_url": result.source_url,
                    "timestamp": result.timestamp.isoformat(),
                },
                "data": _extract_data(result),
            }

        return {"meta": None, "data": _extract_data(result)}


class CsvFormatter:
    def format(
        self,
        result: ScrapeResult | List[Any],
        *,
        fieldnames: Optional[Sequence[str]] = None,
    ) -> str:
        data = _extract_data(result)
        if not data:
            return ""

        if fieldnames is None:
            keys: List[str] = []
            for row in data:
                for key in row.keys():
                    if key not in keys:
                        keys.append(key)
            fieldnames = keys

        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=fieldnames)
        writer.writeheader()
        for row in data:
            writer.writerow(row)
        return output.getvalue()


class PandasDataFrameFormatter:
    def format(self, result: ScrapeResult | List[Any]):
        if not _HAS_PANDAS:
            warnings.warn(
                "Pandas nie jest zainstalowane. Zwracam surową listę rekordów; "
                "użyj eksportu do JSON/CSV lub doinstaluj pandas.",
                RuntimeWarning,
            )
            return _extract_data(result)
        return pd.DataFrame(_extract_data(result))
