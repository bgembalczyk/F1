from __future__ import annotations

from pathlib import Path
from typing import Optional, Sequence

from scrapers.base.formatters import (
    CsvFormatter,
    JsonFormatter,
    PandasDataFrameFormatter,
)
from scrapers.base.results import ScrapeResult
from scrapers.base.types import ExportableRecord


class DataExporter:
    def __init__(
        self,
        *,
        json_formatter: JsonFormatter | None = None,
        csv_formatter: CsvFormatter | None = None,
        dataframe_formatter: PandasDataFrameFormatter | None = None,
    ) -> None:
        self._json_formatter = json_formatter or JsonFormatter()
        self._csv_formatter = csv_formatter or CsvFormatter()
        self._dataframe_formatter = dataframe_formatter or PandasDataFrameFormatter()

    def to_json(
        self,
        result: ScrapeResult | list[ExportableRecord],
        path: str | Path,
        *,
        indent: int = 2,
        include_metadata: bool = False,
    ) -> None:
        payload = self._json_formatter.format(
            result, indent=indent, include_metadata=include_metadata
        )
        path = Path(path)
        path.write_text(payload, encoding="utf-8")

    def to_csv(
        self,
        result: ScrapeResult | list[ExportableRecord],
        path: str | Path,
        *,
        fieldnames: Optional[Sequence[str]] = None,
    ) -> None:
        payload = self._csv_formatter.format(result, fieldnames=fieldnames)
        if not payload:
            return
        path = Path(path)
        path.write_text(payload, encoding="utf-8")

    def to_dataframe(self, result: ScrapeResult | list[ExportableRecord]):
        return self._dataframe_formatter.format(result)
