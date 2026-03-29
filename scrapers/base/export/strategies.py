from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path
from typing import TYPE_CHECKING
from typing import Any

from scrapers.base.format.pandas_formatter import PandasDataFrameFormatter

if TYPE_CHECKING:
    from scrapers.base.export.exporters import DataExporter
    from scrapers.base.results import ScrapeResult


class JsonExportStrategy:
    def export(
        self,
        result: "ScrapeResult",
        *,
        exporter: "DataExporter",
        path: str | Path,
        indent: int = 2,
        include_metadata: bool = False,
    ) -> None:
        exporter.to_json(
            result,
            path,
            indent=indent,
            include_metadata=include_metadata,
        )


class CsvExportStrategy:
    def export(
        self,
        result: "ScrapeResult",
        *,
        exporter: "DataExporter",
        path: str | Path,
        fieldnames: Sequence[str] | None = None,
        include_metadata: bool = False,
    ) -> None:
        exporter.to_csv(
            result,
            path,
            fieldnames=fieldnames,
            include_metadata=include_metadata,
        )


class DataFrameExportStrategy:
    def export(self, result: "ScrapeResult") -> Any:
        return PandasDataFrameFormatter().format(result)
