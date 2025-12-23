from __future__ import annotations

from datetime import datetime, timezone
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional, Sequence, TYPE_CHECKING

from scrapers.base.format.pandas_formatter import PandasDataFrameFormatter
from scrapers.base.normalization import NormalizationRule, RecordNormalizer
from scrapers.base.records import ExportRecord

if TYPE_CHECKING:
    from scrapers.base.export.exporters import DataExporter


@dataclass(frozen=True)
class ScrapeResult:
    data: List[ExportRecord]
    source_url: Optional[str]
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def _with_normalized_data(
        self,
        *,
        normalize_keys: bool,
        normalization_rules: Sequence[NormalizationRule] | None,
    ) -> "ScrapeResult":
        normalizer = RecordNormalizer(
            normalize_keys=normalize_keys,
            normalization_rules=normalization_rules,
        )
        if not normalizer.has_rules:
            return self

        normalized: list[ExportRecord] = []
        for item in self.data:
            if isinstance(item, dict):
                normalized.append(normalizer.normalize_record(item))
            else:
                normalized.append(item)

        return ScrapeResult(
            data=normalized,
            source_url=self.source_url,
            timestamp=self.timestamp,
        )

    def to_json(
        self,
        path: str | Path,
        *,
        exporter: "DataExporter | None" = None,
        indent: int = 2,
        include_metadata: bool = False,
        normalize_keys: bool = False,
        normalization_rules: Sequence[NormalizationRule] | None = None,
    ) -> None:
        normalized = self._with_normalized_data(
            normalize_keys=normalize_keys,
            normalization_rules=normalization_rules,
        )
        exporter = self._resolve_exporter(exporter)
        exporter.to_json(
            normalized,
            path,
            indent=indent,
            include_metadata=include_metadata,
        )

    def to_csv(
        self,
        path: str | Path,
        *,
        exporter: "DataExporter | None" = None,
        fieldnames: Sequence[str] | None = None,
        fieldnames_strategy: str = "union",
        normalize_keys: bool = False,
        normalization_rules: Sequence[NormalizationRule] | None = None,
    ) -> None:
        from scrapers.base.export.export_helpers import (
            fieldnames_from_first_row,
            fieldnames_from_union,
        )
        from scrapers.base.format.formatter_helpers import extract_data

        normalized = self._with_normalized_data(
            normalize_keys=normalize_keys,
            normalization_rules=normalization_rules,
        )

        if fieldnames is None:
            data = extract_data(normalized)
            if data:
                if fieldnames_strategy == "union":
                    fieldnames = fieldnames_from_union(data)
                elif fieldnames_strategy == "first_row":
                    fieldnames = fieldnames_from_first_row(data)
                else:
                    raise ValueError(
                        "Nieznana strategia fieldnames: "
                        f"{fieldnames_strategy!r}. Dostępne: 'union', 'first_row'."
                    )

        exporter = self._resolve_exporter(exporter)
        exporter.to_csv(normalized, path, fieldnames=fieldnames)

    def to_dataframe(
        self,
        *,
        normalize_keys: bool = False,
        normalization_rules: Sequence[NormalizationRule] | None = None,
    ):
        normalized = self._with_normalized_data(
            normalize_keys=normalize_keys,
            normalization_rules=normalization_rules,
        )
        return PandasDataFrameFormatter().format(normalized)

    @staticmethod
    def _resolve_exporter(exporter: "DataExporter | None") -> "DataExporter":
        from scrapers.base.export.exporters import DataExporter

        return exporter or DataExporter()
