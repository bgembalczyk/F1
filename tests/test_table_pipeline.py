from dataclasses import dataclass

import pytest

pytest.importorskip("bs4")

from bs4 import BeautifulSoup

from scrapers.base.table.columns.types.auto import AutoColumn
from scrapers.base.table.config import ScraperConfig
from scrapers.base.table.pipeline import TablePipeline


def test_table_pipeline_parses_rows_and_filters_repeated_headers():
    html = """
    <table class="wikitable">
        <tr><th>Driver</th><th>Time</th></tr>
        <tr><th>Driver</th><th>Time</th></tr>
        <tr><td>Max Verstappen</td><td>1:20.000</td></tr>
    </table>
    """
    soup = BeautifulSoup(html, "html.parser")
    config = ScraperConfig(
        url="https://example.com",
        expected_headers=["Driver", "Time"],
        column_map={"Driver": "driver"},
        columns={"driver": AutoColumn(), "time": AutoColumn()},
    )

    pipeline = TablePipeline(
        config=config,
        include_urls=False,
    )

    assert pipeline.parse_soup(soup) == [
        {
            "driver": "Max Verstappen",
            "time": "1:20.000",
        },
    ]


def test_table_pipeline_maps_columns_for_cells():
    html = """
    <table class="wikitable">
        <tr><th>Driver</th><th>Team</th></tr>
        <tr><td>Lewis Hamilton</td><td>Mercedes</td></tr>
    </table>
    """
    soup = BeautifulSoup(html, "html.parser")
    cells = soup.find_all("td")
    headers = ["Driver", "Team"]

    config = ScraperConfig(
        url="https://example.com",
        column_map={"Driver": "driver_name"},
        columns={"driver_name": AutoColumn(), "team": AutoColumn()},
    )
    pipeline = TablePipeline(
        config=config,
        include_urls=False,
    )

    assert pipeline.parse_cells(headers, cells) == {
        "driver_name": "Lewis Hamilton",
        "team": "Mercedes",
    }


def test_table_pipeline_normalize_cell_maps_header_and_cleans_text():
    html = "<table><tr><td>Lewis Hamilton [1]</td></tr></table>"
    soup = BeautifulSoup(html, "html.parser")
    cell = soup.find("td")
    config = ScraperConfig(
        url="https://example.com",
        column_map={"Driver": "driver_name"},
        columns={"driver_name": AutoColumn()},
    )
    pipeline = TablePipeline(
        config=config,
        include_urls=False,
    )

    key, raw_text, clean_text = pipeline._normalize_cell("Driver", cell)

    assert key == "driver_name"
    assert raw_text == "Lewis Hamilton [1]"
    assert clean_text == "Lewis Hamilton"


def test_table_pipeline_extract_links_respects_include_urls_flag():
    html = '<table><tr><td><a href="/wiki/Lewis">Lewis</a></td></tr></table>'
    soup = BeautifulSoup(html, "html.parser")
    cell = soup.find("td")
    config = ScraperConfig(
        url="https://example.com",
        columns={"driver": AutoColumn()},
    )
    pipeline = TablePipeline(
        config=config,
        include_urls=False,
    )

    assert pipeline._extract_links(cell) == []


def test_table_pipeline_applies_record_factory():
    @dataclass
    class DriverRecord:
        driver: str
        time: str

    html = """
    <table class="wikitable">
        <tr><th>Driver</th><th>Time</th></tr>
        <tr><td>Max Verstappen</td><td>1:20.000</td></tr>
    </table>
    """
    soup = BeautifulSoup(html, "html.parser")
    config = ScraperConfig(
        url="https://example.com",
        expected_headers=["Driver", "Time"],
        columns={"driver": AutoColumn(), "time": AutoColumn()},
        record_factory=DriverRecord,
    )
    pipeline = TablePipeline(
        config=config,
        include_urls=False,
    )

    records = pipeline.parse_soup(soup)

    assert records == [DriverRecord(driver="Max Verstappen", time="1:20.000")]
