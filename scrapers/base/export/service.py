from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path
from typing import Any

from scrapers.base.export.contracts import DataFrameFormatterProtocol
from scrapers.base.export.contracts import ExporterProtocol
from scrapers.base.export.contracts import FieldnamesStrategyProtocol
from scrapers.base.format.formatter_helpers import extract_data


class ExportService:
    def __init__(
        self,
        *,
        exporter: ExporterProtocol,
        fieldnames_strategy: FieldnamesStrategyProtocol,
        dataframe_formatter: DataFrameFormatterProtocol,
    ) -> None:
        self._exporter = exporter
        self._fieldnames_strategy = fieldnames_strategy
        self._dataframe_formatter = dataframe_formatter

    def to_json(
        self,
        result,
        path: str | Path,
        *,
        exporter: ExporterProtocol | None = None,
        indent: int = 2,
        include_metadata: bool = False,
    ) -> None:
        active_exporter = exporter or self._exporter
        active_exporter.to_json(
            result,
            path,
            indent=indent,
            include_metadata=include_metadata,
        )

    def to_csv(
        self,
        result,
        path: str | Path,
        *,
        exporter: ExporterProtocol | None = None,
        fieldnames: Sequence[str] | None = None,
        fieldnames_strategy: str = "union",
        include_metadata: bool = False,
    ) -> None:
        resolved_fieldnames = fieldnames
        if resolved_fieldnames is None:
            data = extract_data(result)
            if data:
                resolved_fieldnames = self._fieldnames_strategy.resolve(
                    data,
                    strategy=fieldnames_strategy,
                )

        active_exporter = exporter or self._exporter
        active_exporter.to_csv(
            result,
            path,
            fieldnames=resolved_fieldnames,
            include_metadata=include_metadata,
        )

    def to_dataframe(self, result) -> Any:
        return self._dataframe_formatter.format(result)
