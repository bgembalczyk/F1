from __future__ import annotations

import typing
from dataclasses import dataclass
from dataclasses import field
from datetime import datetime
from datetime import timezone

from infrastructure.export.default_export_service import build_default_export_service
from scrapers.base.normalization import NormalizationRule
from scrapers.base.normalization import RecordNormalizer

if typing.TYPE_CHECKING:
    from collections.abc import Sequence
    from pathlib import Path

    from scrapers.base.export.contracts import ExporterProtocol
    from scrapers.base.export.service import ExportService
    from validation.validator_base import ExportRecord


def _create_export_service() -> ExportService:
    # di-antipattern-allow: local import by design.
    from scrapers.base.export.exporters import DataExporter
    from scrapers.base.export.fieldnames import FieldnamesStrategySelector
    from scrapers.base.export.service import ExportService as _ExportService
    from scrapers.base.format.pandas_formatter import PandasDataFrameFormatter

    return _ExportService(
        exporter=DataExporter(),
        fieldnames_strategy=FieldnamesStrategySelector(),
        dataframe_formatter=PandasDataFrameFormatter(),
    )


@dataclass(frozen=True)
class ScrapeResult:
    data: list[ExportRecord]
    source_url: str | None
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    export_service: ExportService = field(default_factory=_create_export_service)

    def _with_normalized_data(
        self,
        *,
        normalize_keys: bool,
        normalization_rules: Sequence[NormalizationRule] | None,
    ) -> ScrapeResult:
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
            export_service=self.export_service,
        )

    def to_json(
        self,
        path: str | Path,
        *,
        exporter: ExporterProtocol | None = None,
        indent: int = 2,
        normalize_keys: bool = False,
        normalization_rules: Sequence[NormalizationRule] | None = None,
        include_metadata: bool = False,
    ) -> None:
        normalized = self._with_normalized_data(
            normalize_keys=normalize_keys,
            normalization_rules=normalization_rules,
        )
        self.export_service.to_json(
            normalized,
            path,
            exporter=exporter,
            indent=indent,
            include_metadata=include_metadata,
        )

    def to_csv(
        self,
        path: str | Path,
        *,
        exporter: ExporterProtocol | None = None,
        fieldnames: Sequence[str] | None = None,
        fieldnames_strategy: str = "union",
        normalize_keys: bool = False,
        normalization_rules: Sequence[NormalizationRule] | None = None,
        include_metadata: bool = False,
    ) -> None:
        normalized = self._with_normalized_data(
            normalize_keys=normalize_keys,
            normalization_rules=normalization_rules,
        )

        self.export_service.to_csv(
            normalized,
            path,
            exporter=exporter,
            fieldnames=fieldnames,
            fieldnames_strategy=fieldnames_strategy,
            include_metadata=include_metadata,
        )

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
        return self.export_service.to_dataframe(normalized)
