from __future__ import annotations

from pathlib import Path
from typing import Optional, Sequence

from scrapers.base.format.csv_formatter import CsvFormatter
from scrapers.base.format.json_formatter import JsonFormatter
from scrapers.base.results import ScrapeResult


class DataExporter:
    def __init__(
        self,
        *,
        json_formatter: JsonFormatter | None = None,
        csv_formatter: CsvFormatter | None = None,
    ) -> None:
        self._json_formatter = json_formatter or JsonFormatter()
        self._csv_formatter = csv_formatter or CsvFormatter()

    def to_json(
        self,
        result: ScrapeResult,
        path: str | Path,
        *,
        indent: int = 2,
        include_metadata: bool = False,
    ) -> None:
        payload = self._json_formatter.format(
            result,
            indent=indent,
            include_metadata=include_metadata,
        )
        Path(path).write_text(payload, encoding="utf-8")

    def to_csv(
        self,
        result: ScrapeResult,
        path: str | Path,
        *,
        fieldnames: Optional[Sequence[str]] = None,
    ) -> None:
        payload = self._csv_formatter.format(result, fieldnames=fieldnames)
        if not payload:
            return

        Path(path).write_text(payload, encoding="utf-8")
