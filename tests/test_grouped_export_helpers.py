from pathlib import Path
from typing import Any

from scrapers.base.export.export_helpers import export_grouped_json


class _StubLogger:
    def __init__(self) -> None:
        self.messages: list[tuple[str, int]] = []

    def info(self, msg: str, count: int) -> None:
        self.messages.append((msg, count))


class _StubScraper:
    def __init__(self) -> None:
        self.logger = _StubLogger()
        self.url = "https://example.com"
        self.exporter = None


def test_export_grouped_json_writes_files_and_uses_other_fallback(
    tmp_path: Path,
) -> None:
    scraper = _StubScraper()
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

    export_grouped_json(scraper, data, tmp_path, key_fn)

    assert (tmp_path / "A.json").exists()
    assert (tmp_path / "B.json").exists()
    assert (tmp_path / "other.json").exists()
    assert scraper.logger.messages == [("Pobrano rekordów: %s", 3)]
