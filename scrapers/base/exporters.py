from __future__ import annotations

import re
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Sequence

from scrapers.base.formatters import (
    CsvFormatter,
    JsonFormatter,
    PandasDataFrameFormatter,
)
from scrapers.base.records import ExportRecord
from scrapers.base.results import ScrapeResult

NormalizationRule = Callable[[Dict[str, Any]], Dict[str, Any]]


class DataExporter:
    def __init__(
        self,
        *,
        json_formatter: JsonFormatter | None = None,
        csv_formatter: CsvFormatter | None = None,
        dataframe_formatter: PandasDataFrameFormatter | None = None,
        normalize_keys: bool = False,
        normalization_rules: Sequence[NormalizationRule] | None = None,
    ) -> None:
        self._json_formatter = json_formatter or JsonFormatter()
        self._csv_formatter = csv_formatter or CsvFormatter()
        self._dataframe_formatter = dataframe_formatter or PandasDataFrameFormatter()
        self._normalization_rules = self._build_normalization_rules(
            normalize_keys=normalize_keys,
            normalization_rules=normalization_rules,
        )

    @staticmethod
    def _build_normalization_rules(
        *,
        normalize_keys: bool,
        normalization_rules: Sequence[NormalizationRule] | None,
    ) -> List[NormalizationRule]:
        rules: List[NormalizationRule] = []
        if normalize_keys:
            rules.append(_normalize_record_keys)
            rules.append(_drop_empty_fields)
        if normalization_rules:
            rules.extend(normalization_rules)
        return rules

    def _apply_normalization(
        self, result: ScrapeResult | List[ExportRecord]
    ) -> ScrapeResult | List[ExportRecord]:
        if not self._normalization_rules:
            return result

        data = _extract_data(result)
        normalized: List[ExportRecord] = []

        for record in data:
            # ExportRecord jest w praktyce dict-like; normalizacja działa na dict[str, Any]
            updated: Dict[str, Any] = dict(record)
            for rule in self._normalization_rules:
                updated = rule(updated)
            normalized.append(updated)  # type: ignore[arg-type]

        if isinstance(result, ScrapeResult):
            return ScrapeResult(
                data=normalized,  # type: ignore[arg-type]
                source_url=result.source_url,
                timestamp=result.timestamp,
            )

        return normalized

    def to_json(
        self,
        result: ScrapeResult | List[ExportRecord],
        path: str | Path,
        *,
        indent: int = 2,
        include_metadata: bool = False,
    ) -> None:
        payload = self._json_formatter.format(
            self._apply_normalization(result),
            indent=indent,
            include_metadata=include_metadata,
        )
        Path(path).write_text(payload, encoding="utf-8")

    def to_csv(
        self,
        result: ScrapeResult | List[ExportRecord],
        path: str | Path,
        *,
        fieldnames: Optional[Sequence[str]] = None,
        fieldnames_strategy: str = "union",
    ) -> None:
        """
        Zapisz dane do CSV.

        - Jeśli fieldnames podane -> używamy wprost.
        - Jeśli fieldnames == None:
            - strategy="union": stabilna unia kluczy z kolejnych rekordów
            - strategy="first_row": tylko klucze z pierwszego rekordu
        """
        normalized = self._apply_normalization(result)
        data = _extract_data(normalized)
        if not data:
            return

        if fieldnames is None:
            if fieldnames_strategy == "union":
                fieldnames = _fieldnames_from_union(data)
            elif fieldnames_strategy == "first_row":
                fieldnames = _fieldnames_from_first_row(data)
            else:
                raise ValueError(
                    "Nieznana strategia fieldnames: "
                    f"{fieldnames_strategy!r}. Dostępne: 'union', 'first_row'."
                )

        payload = self._csv_formatter.format(normalized, fieldnames=fieldnames)
        if not payload:
            return

        Path(path).write_text(payload, encoding="utf-8")

    def to_dataframe(self, result: ScrapeResult | List[ExportRecord]):
        return self._dataframe_formatter.format(self._apply_normalization(result))


def _extract_data(result: ScrapeResult | List[ExportRecord]) -> List[ExportRecord]:
    if isinstance(result, ScrapeResult):
        return result.data  # type: ignore[return-value]
    return result


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
