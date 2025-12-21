from __future__ import annotations

from pathlib import Path
from typing import Any, Optional, Sequence

from scrapers.base.formatters import (
    CsvFormatter,
    JsonFormatter,
    PandasDataFrameFormatter,
)
from scrapers.base.results import ScrapeResult
from scrapers.base.export_helpers import (
    ExportRecord,
    NormalizationRule,
    _extract_data,
    _normalize_record_keys,
    _drop_empty_fields,
    _fieldnames_from_union,
    _fieldnames_from_first_row,
)


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
    ) -> list[NormalizationRule]:
        rules: list[NormalizationRule] = []
        if normalize_keys:
            rules.append(_normalize_record_keys)
            rules.append(_drop_empty_fields)
        if normalization_rules:
            rules.extend(normalization_rules)
        return rules

    def _apply_normalization(
        self, result: ScrapeResult | list[Any]
    ) -> ScrapeResult | list[Any]:
        """
        Normalizacja działa TYLKO dla listy rekordów dict-like.

        Jeśli data zawiera obiekty niebędące mappingiem — pozostawiamy je bez zmian
        (kompatybilność ze ścieżkami, gdzie formatter sam potrafi serializować).
        """
        if not self._normalization_rules:
            return result

        data = _extract_data(result)

        normalized: list[Any] = []
        for item in data:
            if not isinstance(item, dict):
                normalized.append(item)
                continue

            updated: dict[str, Any] = dict(item)
            for rule in self._normalization_rules:
                updated = rule(updated)
            normalized.append(updated)

        if isinstance(result, ScrapeResult):
            return ScrapeResult(
                data=normalized,  # type: ignore[arg-type]
                source_url=result.source_url,
                timestamp=result.timestamp,
            )
        return normalized

    def to_json(
        self,
        result: ScrapeResult | list[Any],
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
        result: ScrapeResult | list[Any],
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

    def to_dataframe(self, result: ScrapeResult | list[Any]):
        return self._dataframe_formatter.format(self._apply_normalization(result))
