import importlib.util
import json
from typing import Any

import pytest


def test_quality_report_includes_metadata(tmp_path) -> None:
    if importlib.util.find_spec("bs4") is None:  # pragma: no cover - depends on env
        pytest.skip("bs4 is not available")
    if importlib.util.find_spec("certifi") is None:  # pragma: no cover - depends on env
        pytest.skip("certifi is not available")

    from scrapers.base.ABC import F1Scraper
    from scrapers.base.options import ScraperOptions
    from validation.records import RecordValidator

    class _DummyValidator(RecordValidator):
        def validate(self, record):  # type: ignore[override]
            return []

    class _DummyScraper(F1Scraper):
        url = "https://example.com"

        def _download(self) -> str:
            return "<html></html>"

        def _parse_soup(self, soup: Any):
            return [{"name": "A"}, {"name": "B"}]

    options = ScraperOptions(
        validator=_DummyValidator(),
        debug_dir=tmp_path,
        quality_report=True,
    )
    scraper = _DummyScraper(options=options)

    scraper.fetch()

    report_path = tmp_path / "quality_report.json"
    report = json.loads(report_path.read_text(encoding="utf-8"))

    assert "meta" in report
    meta = report["meta"]
    assert meta["record_counts"]["parse"] == 2
    assert meta["record_counts"]["normalize"] == 2
    assert meta["record_counts"]["transform"] == 2
    assert meta["record_counts"]["validate"] == 2
    assert "timings" in meta
    assert "parse" in meta["timings"]
