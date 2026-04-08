from pathlib import Path
from typing import Any

from scrapers.base.services.result_export_service import ResultExportService


class StubLogger:
    def __init__(self) -> None:
        self.messages: list[tuple[str, int]] = []

    def info(self, msg: str, count: int) -> None:
        self.messages.append((msg, count))


class StubScraper:
    def __init__(self) -> None:
        self.logger = StubLogger()
        self.url = "https://example.com"
        self.exporter = None


def test_export_grouped_json_writes_files_and_uses_other_fallback(
    tmp_path: Path,
) -> None:
    scraper = StubScraper()
    data: list[dict[str, Any]] = [
        {"name": "Alpha"},
        {"name": ""},
        {"name": "Beta"},
    ]

    def key_fn(record: dict[str, Any]) -> str:
        name = record.get("name", "")
        if not name:
            return ""
        return name[0].upper()

    ResultExportService().export_grouped_json(scraper, data, tmp_path, key_fn)

    assert (tmp_path / "A.json").exists()
    assert (tmp_path / "B.json").exists()
    assert (tmp_path / "other.json").exists()
    assert scraper.logger.messages == [("Pobrano rekordów: %s", 3)]
