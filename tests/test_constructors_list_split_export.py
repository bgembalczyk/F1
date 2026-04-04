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
