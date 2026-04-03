from collections.abc import Sequence
from pathlib import Path
from typing import TYPE_CHECKING

from scrapers.base.format.csv_formatter import CsvFormatter
from scrapers.base.format.json_formatter import JsonFormatter

if TYPE_CHECKING:
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
        result: "ScrapeResult",
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
        self._write_payload(path, payload)

    def to_csv(
        self,
        result: "ScrapeResult",
        path: str | Path,
        *,
        fieldnames: Sequence[str] | None = None,
        include_metadata: bool = False,
    ) -> None:
        payload = self._csv_formatter.format(
            result,
            fieldnames=fieldnames,
            include_metadata=include_metadata,
        )
        self._write_payload(path, payload)

    def _write_payload(self, path: str | Path, payload: str) -> None:
        output_path = self._normalize_path(path)
        output_path.write_text(payload, encoding="utf-8")

    @staticmethod
    def _normalize_path(path: str | Path) -> Path:
        output_path = Path(path)
        if output_path.exists() and output_path.is_dir():
            msg = f"Expected file path, got directory: {output_path}"
            raise IsADirectoryError(msg)
        return output_path
