from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from dataclasses import field
from datetime import datetime
from datetime import timezone
from pathlib import Path
from typing import TYPE_CHECKING

from scrapers.base.normalization import NormalizationRule
from validation.validator_base import ExportRecord

if TYPE_CHECKING:
    from scrapers.base.export.exporters import DataExporter


@dataclass(frozen=True)
class PreparedExport:
    result: "ScrapeResult"
    fieldnames: Sequence[str] | None = None


@dataclass(frozen=True)
class ScrapeResult:
    data: list[ExportRecord]
    source_url: str | None
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def _with_normalized_data(
        self,
        *,
        normalize_keys: bool,
        normalization_rules: Sequence[NormalizationRule] | None,
    ) -> "ScrapeResult":
        from scrapers.base.normalization import RecordNormalizer

        normalizer = RecordNormalizer(
            normalize_keys=normalize_keys,
            normalization_rules=normalization_rules,
        )
        if not normalizer.has_rules:
            return self

        normalized = normalizer.normalize(self.data)

        return ScrapeResult(
            data=normalized,
            source_url=self.source_url,
            timestamp=self.timestamp,
        )

    def prepare_for_export(
        self,
        *,
        normalize_keys: bool = False,
        normalization_rules: Sequence[NormalizationRule] | None = None,
        fieldnames: Sequence[str] | None = None,
        fieldnames_strategy: str = "union",
    ) -> PreparedExport:
        from scrapers.base.export.export_helpers import fieldnames_from_first_row
        from scrapers.base.export.export_helpers import fieldnames_from_union
        from scrapers.base.format.formatter_helpers import extract_data

        normalized = self._with_normalized_data(
            normalize_keys=normalize_keys,
            normalization_rules=normalization_rules,
        )

        resolved_fieldnames = fieldnames
        if resolved_fieldnames is None:
            data = extract_data(normalized)
            if data:
                if fieldnames_strategy == "union":
                    resolved_fieldnames = fieldnames_from_union(data)
                elif fieldnames_strategy == "first_row":
                    resolved_fieldnames = fieldnames_from_first_row(data)
                else:
                    msg = (
                        "Nieznana strategia fieldnames: "
                        f"{fieldnames_strategy!r}. Dostępne: 'union', 'first_row'."
                    )
                    raise ValueError(msg)

        return PreparedExport(result=normalized, fieldnames=resolved_fieldnames)

    def to_json(
        self,
        path: str | Path,
        *,
        exporter: "DataExporter | None" = None,
        indent: int = 2,
        normalize_keys: bool = False,
        normalization_rules: Sequence[NormalizationRule] | None = None,
        include_metadata: bool = False,
    ) -> None:
        from scrapers.base.export.strategies import JsonExportStrategy

        prepared = self.prepare_for_export(
            normalize_keys=normalize_keys,
            normalization_rules=normalization_rules,
        )
        strategy = JsonExportStrategy()
        strategy.export(
            prepared.result,
            exporter=self._resolve_exporter(exporter),
            path=path,
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
        include_metadata: bool = False,
    ) -> None:
        from scrapers.base.export.strategies import CsvExportStrategy

        prepared = self.prepare_for_export(
            normalize_keys=normalize_keys,
            normalization_rules=normalization_rules,
            fieldnames=fieldnames,
            fieldnames_strategy=fieldnames_strategy,
        )

        strategy = CsvExportStrategy()
        strategy.export(
            prepared.result,
            exporter=self._resolve_exporter(exporter),
            path=path,
            fieldnames=prepared.fieldnames,
            include_metadata=include_metadata,
        )

    def to_dataframe(
        self,
        *,
        normalize_keys: bool = False,
        normalization_rules: Sequence[NormalizationRule] | None = None,
    ):
        from scrapers.base.export.strategies import DataFrameExportStrategy

        prepared = self.prepare_for_export(
            normalize_keys=normalize_keys,
            normalization_rules=normalization_rules,
        )
        strategy = DataFrameExportStrategy()
        return strategy.export(prepared.result)

    @staticmethod
    def _resolve_exporter(exporter: "DataExporter | None") -> "DataExporter":
        from scrapers.base.export.exporters import DataExporter

        return exporter or DataExporter()
