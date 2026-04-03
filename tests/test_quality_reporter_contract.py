# ruff: noqa: PLR2004
from __future__ import annotations

import json
from typing import TYPE_CHECKING
from typing import Any

from scrapers.base.abc import ABCScraper
from scrapers.base.options import ScraperOptions
from scrapers.base.quality.reporter import QualityReporter

if TYPE_CHECKING:
    from pathlib import Path

    from bs4 import BeautifulSoup


class DummyFetcher:
    def __init__(self, html: str) -> None:
        self.html = html
        self.http_client = object()

    def get(self, _url: str) -> str:
        return self.html

    def set_cache(self, _cache_adapter: object) -> None:
        return None


class DummyContractScraper(ABCScraper):
    url = "https://example.com/domain"

    def _parse_soup(self, _soup: BeautifulSoup) -> list[dict[str, Any]]:
        return [
            {"name": "alpha", "url": "https://example.com/a", "country": "PL"},
            {"name": "alpha", "url": "https://example.com/a", "country": ""},
        ]


class DummyDiffScraper(ABCScraper):
    url = "https://example.com/diff"

    def _parse_soup(self, _soup: BeautifulSoup) -> list[dict[str, Any]]:
        return [
            {"id": "driver-1", "name": "Alpha", "country": "PL"},
            {"id": "driver-2", "name": "Beta", "country": ""},
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
        assert payload["missing_fields"]["country"] == 1
        assert payload["duplicate_keys"]["Ayrton"] == 2
        assert payload["source_metadata"]["domain"] == domain


def test_debug_mode_writes_compact_diffs_with_metadata(tmp_path: Path) -> None:
    scraper = DummyDiffScraper(
        options=ScraperOptions(
            fetcher=DummyFetcher("<html></html>"),
            quality_report=True,
            debug_dir=tmp_path / "data" / "debug",
            run_id="diff-42",
            debug_diff_record_ids={"driver-2"},
        ),
    )

    scraper.fetch()

    diff_path = tmp_path / "data" / "debug" / "debug_step_diffs_diff-42.jsonl"
    assert diff_path.exists()
    lines = [
        json.loads(line)
        for line in diff_path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    assert lines
    assert all(line["stage"] for line in lines)
    assert all(line["domain"] == "test_quality_reporter_contract" for line in lines)
    assert all(line["source"] == "https://example.com/diff" for line in lines)
    assert all(line["record_id"] == "driver-2" for line in lines)
    assert all("changed_fields" in line for line in lines)


def test_debug_mode_diff_filter_by_domain(tmp_path: Path) -> None:
    scraper = DummyDiffScraper(
        options=ScraperOptions(
            fetcher=DummyFetcher("<html></html>"),
            quality_report=True,
            debug_dir=tmp_path / "data" / "debug",
            run_id="diff-domain-filter",
            debug_diff_domains={"drivers"},
        ),
    )

    scraper.fetch()

    diff_path = (
        tmp_path / "data" / "debug" / "debug_step_diffs_diff-domain-filter.jsonl"
    )
    assert not diff_path.exists()


def test_quality_report_is_generated_automatically_for_pipeline_steps(
    tmp_path: Path,
) -> None:
    scraper = DummyContractScraper(
        options=ScraperOptions(
            fetcher=DummyFetcher("<html></html>"),
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
        assert "missing_fields" in payload
        assert "duplicate_keys" in payload
        assert "source_metadata" in payload
