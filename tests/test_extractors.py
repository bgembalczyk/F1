import logging
import sys
from pathlib import Path

import pytest
from bs4 import BeautifulSoup

from scrapers.base.extractors import InfoboxExtractor
from scrapers.base.extractors import TableExtractor
from scrapers.base.table.columns.types.auto import AutoColumn
from scrapers.base.table.config import ScraperConfig

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))

pytest.importorskip("bs4")


def test_table_extractor_extracts_records_and_logs(
    caplog: pytest.LogCaptureFixture,
) -> None:
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
    )
    extractor = TableExtractor(
        config=config,
        include_urls=False,
    )
    extractor.set_run_id("run-1")

    with caplog.at_level(logging.DEBUG):
        records = extractor.extract(soup)

    assert records == [{"driver": "Max Verstappen", "time": "1:20.000"}]
    assert "TableExtractor extracted 1 record(s)" in caplog.text


def test_infobox_extractor_extracts_rows_and_logs(
    caplog: pytest.LogCaptureFixture,
) -> None:
    html = """
    <table class="infobox">
        <caption>Test Circuit</caption>
        <tr><th>Country</th><td>Testland</td></tr>
    </table>
    """
    soup = BeautifulSoup(html, "html.parser")
    extractor = InfoboxExtractor(run_id="run-2")

    with caplog.at_level(logging.DEBUG):
        record = extractor.extract(soup)

    assert record["title"] == "Test Circuit"
    assert record["rows"]["Country"]["text"] == "Testland"
    assert "InfoboxExtractor extracted 1 row(s)" in caplog.text
