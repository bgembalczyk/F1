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
        full_url=lambda href: href,
        skip_sentinel=object(),
    )

    assert pipeline.parse_soup(soup) == [
        {"driver": "Max Verstappen", "time": "1:20.000"}
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
        full_url=lambda href: href,
        skip_sentinel=object(),
    )

    assert pipeline.parse_cells(headers, cells) == {
        "driver_name": "Lewis Hamilton",
        "team": "Mercedes",
    }
