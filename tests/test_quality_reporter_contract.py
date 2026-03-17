from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from bs4 import BeautifulSoup

from scrapers.base.abc import ABCScraper
from scrapers.base.options import ScraperOptions
from scrapers.base.quality.reporter import QualityReporter


class DummySourceAdapter:
    def __init__(self, html: str) -> None:
        self.html = html

    def get(self, _url: str) -> str:
        return self.html


class DummyContractScraper(ABCScraper):
    url = "https://example.com/domain"

    def _parse_soup(self, _soup: BeautifulSoup) -> list[dict[str, Any]]:
        return [
            {"name": "alpha", "url": "https://example.com/a", "country": "PL"},
            {"name": "alpha", "url": "https://example.com/a", "country": ""},
        ]


def test_quality_reporter_contract_for_multiple_domains(tmp_path: Path) -> None:
    for domain in ("drivers", "constructors"):
        reporter = QualityReporter(
            report_root=tmp_path / "data" / "checkpoints",
            run_id="run-contract",
            source_metadata={
                "domain": domain,
                "scraper": f"{domain.title()}Scraper",
                "primary_key": "name",
            },
        )

        report_path = reporter.report_step(
            step_id=f"step_1_layer0_{domain}",
            records=[
                {"name": "Ayrton", "country": "BR"},
                {"name": "Ayrton", "country": ""},
            ],
        )

        payload = json.loads(report_path.read_text(encoding="utf-8"))
        assert payload["schema_version"] == "1.0"
        assert payload["record_count"] == 2
        assert payload["null_rate"] == 0.25
        assert payload["missing_fields"]["country"] == 1
        assert payload["duplicate_keys"]["Ayrton"] == 2
        assert payload["duplicate_logical_key_count"] == 1
        assert payload["source_metadata"]["domain"] == domain


def test_quality_report_is_generated_automatically_for_pipeline_steps(
    tmp_path: Path,
) -> None:
    scraper = DummyContractScraper(
        options=ScraperOptions(
            source_adapter=DummySourceAdapter("<html></html>"),
            quality_report=True,
            debug_dir=tmp_path / "data" / "debug",
            run_id="step-42",
        ),
    )

    records = scraper.fetch()

    assert len(records) == 2
    expected_steps = [
        "download",
        "parse",
        "normalize",
        "transform",
        "post_process",
    ]
    for step in expected_steps:
        report_path = (
            tmp_path / "data" / "debug" / f"quality_report_step_step-42_{step}.json"
        )
        assert report_path.exists()
        payload = json.loads(report_path.read_text(encoding="utf-8"))
        assert payload["schema_version"] == "1.0"
        assert "record_count" in payload
        assert "null_rate" in payload
        assert "missing_fields" in payload
        assert "duplicate_keys" in payload
        assert "duplicate_logical_key_count" in payload
        assert "source_metadata" in payload
