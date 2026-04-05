# ruff: noqa: SLF001
from __future__ import annotations

import json

from scrapers.base.options import ScraperOptions
from scrapers.constructors.constructors_list import ConstructorsListScraper


def test_constructors_list_scraper_exports_split_json_files(tmp_path) -> None:
    scraper = ConstructorsListScraper(options=ScraperOptions())
    scraper._data = [{"constructor": "Alpha"}]
    scraper._split_export_records = {
        "current_constructors": [{"constructor": "Alpha"}],
        "former_constructors": [{"constructor": "Beta"}],
        "indianapolis_only_constructors": [{"constructor": "Gamma"}],
        "privateer_teams": [{"constructor": "Delta"}],
    }

    output = tmp_path / "constructors.json"
    scraper.to_json(output)

    assert json.loads(output.read_text(encoding="utf-8")) == [{"constructor": "Alpha"}]
    assert json.loads(
        (tmp_path / "constructors_current_constructors.json").read_text(
            encoding="utf-8",
        ),
    ) == [{"constructor": "Alpha"}]
    assert json.loads(
        (tmp_path / "constructors_former_constructors.json").read_text(
            encoding="utf-8",
        ),
    ) == [{"constructor": "Beta"}]
    assert json.loads(
        (tmp_path / "constructors_indianapolis_only_constructors.json").read_text(
            encoding="utf-8",
        ),
    ) == [{"constructor": "Gamma"}]
    assert json.loads(
        (tmp_path / "constructors_privateer_teams.json").read_text(encoding="utf-8"),
    ) == [{"constructor": "Delta"}]


def test_constructors_list_scraper_exports_split_csv_files(tmp_path) -> None:
    scraper = ConstructorsListScraper(options=ScraperOptions())
    scraper._data = [{"constructor": "Alpha"}]
    scraper._split_export_records = {
        "current_constructors": [{"constructor": "Alpha"}],
        "former_constructors": [{"constructor": "Beta"}],
        "indianapolis_only_constructors": [{"constructor": "Gamma"}],
        "privateer_teams": [{"constructor": "Delta"}],
    }

    output = tmp_path / "constructors.csv"
    scraper.to_csv(output)

    assert output.exists()
    assert (tmp_path / "constructors_current_constructors.csv").exists()
    assert (tmp_path / "constructors_former_constructors.csv").exists()
    assert (tmp_path / "constructors_indianapolis_only_constructors.csv").exists()
    assert (tmp_path / "constructors_privateer_teams.csv").exists()


import pytest


def test_constructors_list_scraper_rejects_invalid_scope() -> None:
    with pytest.raises(ValueError, match="Unsupported export_scope"):
        ConstructorsListScraper(
            options=ScraperOptions(), export_scope="invalid_scope"
        )


def test_constructors_list_scraper_restore_split_export_records() -> None:
    scraper = ConstructorsListScraper(options=ScraperOptions())
    scope_records = {
        "current": [{"constructor": "A"}],
        "former": [{"constructor": "B"}],
        "indianapolis": [{"constructor": "C"}],
        "privateer": [{"constructor": "D"}],
    }
    scraper._restore_split_export_records(scope_records)
    assert scraper._split_export_records["current_constructors"] == [{"constructor": "A"}]
    assert scraper._split_export_records["former_constructors"] == [{"constructor": "B"}]


def test_normalize_privateer_urls_without_include_urls() -> None:
    scraper = ConstructorsListScraper(options=ScraperOptions(include_urls=False))
    records = [
        {"team": "A", "team_url": "/wiki/TeamA"},
        {"team": "B"},
        "not a dict",
    ]
    scraper._normalize_privateer_urls(records)
    assert "team_url" not in records[0]


def test_normalize_privateer_urls_with_include_urls() -> None:
    scraper = ConstructorsListScraper(options=ScraperOptions(include_urls=True))
    records = [
        {"team": "A", "team_url": "/wiki/TeamA"},
        {"team": "B", "team_url": "https://external.com"},
        {"team": "C"},
        "not a dict",
    ]
    scraper._normalize_privateer_urls(records)
    assert records[0]["team_url"].startswith("https://en.wikipedia.org")
    assert records[1]["team_url"] == "https://external.com"


def test_should_include_scope_all_includes_any_scope() -> None:
    scraper = ConstructorsListScraper(options=ScraperOptions(), export_scope="all")
    assert scraper._should_include_scope("current")
    assert scraper._should_include_scope("former")
    assert scraper._should_include_scope("indianapolis")


def test_should_include_scope_current_only_includes_current() -> None:
    scraper = ConstructorsListScraper(options=ScraperOptions(), export_scope="current")
    assert scraper._should_include_scope("current")
    assert not scraper._should_include_scope("former")


def test_export_split_json_skips_empty_records(tmp_path) -> None:
    scraper = ConstructorsListScraper(options=ScraperOptions())
    scraper._split_export_records = {
        "current_constructors": [],
        "former_constructors": [],
        "indianapolis_only_constructors": [],
        "privateer_teams": [],
    }
    path = tmp_path / "output.json"
    # Should not create any split files (all empty)
    scraper._export_split_json(path, indent=2, include_metadata=False)
    assert not (tmp_path / "output_current_constructors.json").exists()


def test_export_split_csv_skips_empty_records(tmp_path) -> None:
    scraper = ConstructorsListScraper(options=ScraperOptions())
    scraper._split_export_records = {
        "current_constructors": [],
        "former_constructors": [],
        "indianapolis_only_constructors": [],
        "privateer_teams": [],
    }
    path = tmp_path / "output.csv"
    # Should not create any split files (all empty)
    scraper._export_split_csv(
        path,
        fieldnames=None,
        fieldnames_strategy="union",
        include_metadata=False,
    )
    assert not (tmp_path / "output_current_constructors.csv").exists()
