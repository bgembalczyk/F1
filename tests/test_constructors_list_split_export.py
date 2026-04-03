# ruff: noqa: SLF001
from __future__ import annotations

import json

from scrapers.base.options import ScraperOptions
from scrapers.constructors.constructors_list import ConstructorsListScraper


def test_constructors_list_scraper_exports_split_json_files(tmp_path) -> None:
    scraper = ConstructorsListScraper(options=ScraperOptions())
    scraper._data = [{"constructor": "Alpha"}]
    scraper._split_export_records = {
        "section_parser": [{"constructor": "Alpha"}],
        "sub_section_parser": [{"constructor": "Beta"}],
    }

    output = tmp_path / "constructors.json"
    scraper.to_json(output)

    assert json.loads(output.read_text(encoding="utf-8")) == [{"constructor": "Alpha"}]
    assert json.loads(
        (tmp_path / "constructors_section_parser.json").read_text(encoding="utf-8"),
    ) == [{"constructor": "Alpha"}]
    assert json.loads(
        (tmp_path / "constructors_sub_section_parser.json").read_text(encoding="utf-8"),
    ) == [{"constructor": "Beta"}]


def test_constructors_list_scraper_exports_split_csv_files(tmp_path) -> None:
    scraper = ConstructorsListScraper(options=ScraperOptions())
    scraper._data = [{"constructor": "Alpha"}]
    scraper._split_export_records = {
        "section_parser": [{"constructor": "Alpha"}],
        "sub_section_parser": [{"constructor": "Beta"}],
    }

    output = tmp_path / "constructors.csv"
    scraper.to_csv(output)

    assert output.exists()
    assert (tmp_path / "constructors_section_parser.csv").exists()
    assert (tmp_path / "constructors_sub_section_parser.csv").exists()
