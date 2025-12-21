from __future__ import annotations

from pathlib import Path
from typing import Any, Optional, Sequence

from scrapers.base.export.export_helpers import (
    _extract_data,
    _fieldnames_from_first_row,
    _fieldnames_from_union,
)
from scrapers.base.format.csv_formatter import CsvFormatter
from scrapers.base.format.json_formatter import JsonFormatter
from scrapers.base.format.pandas_formatter import PandasDataFrameFormatter
from scrapers.base.normalization import NormalizationRule, RecordNormalizer
from scrapers.base.records import ExportRecord
from scrapers.base.results import ScrapeResult


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
        self._record_normalizer = RecordNormalizer(
            normalize_keys=normalize_keys,
            normalization_rules=normalization_rules,
        )

    def _apply_normalization(
        self, result: ScrapeResult | list[ExportRecord]
    ) -> ScrapeResult:
        """
        Normalizacja działa TYLKO dla listy rekordów dict-like.

        Jeśli data zawiera obiekty niebędące mappingiem — pozostawiamy je bez zmian
        (kompatybilność ze ścieżkami, gdzie formatter sam potrafi serializować).
        Lista wejściowa jest zawsze opakowana w ScrapeResult.
        """
        if isinstance(result, ScrapeResult):
            normalized_result = result
        else:
            normalized_result = ScrapeResult(data=list(result), source_url=None)

        if not self._record_normalizer.has_rules:
            return normalized_result

        data = _extract_data(normalized_result)

        normalized: list[Any] = []
        for item in data:
            if not isinstance(item, dict):
                normalized.append(item)
                continue

            normalized.append(self._record_normalizer.normalize_record(item))

        return ScrapeResult(
            data=normalized,  # type: ignore[arg-type]
            source_url=normalized_result.source_url,
            timestamp=normalized_result.timestamp,
        )

    def to_json(
        self,
        result: ScrapeResult | list[ExportRecord],
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
        result: ScrapeResult | list[ExportRecord],
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

        # CSV ma sens tylko dla dict-like rekordów
        dict_rows: list[ExportRecord] = [r for r in data if isinstance(r, dict)]
        if not dict_rows:
            return

        if fieldnames is None:
            if fieldnames_strategy == "union":
                fieldnames = _fieldnames_from_union(dict_rows)
            elif fieldnames_strategy == "first_row":
                fieldnames = _fieldnames_from_first_row(dict_rows)
            else:
                raise ValueError(
                    "Nieznana strategia fieldnames: "
                    f"{fieldnames_strategy!r}. Dostępne: 'union', 'first_row'."
                )

        payload = self._csv_formatter.format(normalized, fieldnames=fieldnames)
        if not payload:
            return

        Path(path).write_text(payload, encoding="utf-8")

    def to_dataframe(self, result: ScrapeResult | list[ExportRecord]):
        return self._dataframe_formatter.format(self._apply_normalization(result))
