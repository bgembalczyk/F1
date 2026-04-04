from bs4 import BeautifulSoup

from scrapers.base.helpers.tables.lap_records import LapRecordsTableScraper
from scrapers.base.single_wiki_article.section_selection_strategy import (
    WikipediaSectionByIdSelectionStrategy,
)
from scrapers.circuits.single_scraper import F1SingleCircuitScraper
from scrapers.circuits.single_scraper import detect_layout_name
from scrapers.circuits.single_scraper import is_lap_record_table


def test_select_section_returns_fragment_section_only() -> None:
    scraper = object.__new__(F1SingleCircuitScraper)
    scraper.section_selection_strategy = WikipediaSectionByIdSelectionStrategy(
        domain="circuits",
    )
    soup = BeautifulSoup(
        """
        <h2 id="History">History</h2>
        <p>Some history text.</p>
        <h2 id="Legacy">Legacy</h2>
        <p>Legacy text.</p>
        """,
        "html.parser",
    )

    section = scraper._select_section(soup, "History")  # noqa: SLF001

    assert "Some history text." in section.get_text(" ")
    assert "Legacy text." not in section.get_text(" ")


def test_select_section_returns_full_soup_when_missing_fragment() -> None:
    scraper = object.__new__(F1SingleCircuitScraper)
    scraper.section_selection_strategy = WikipediaSectionByIdSelectionStrategy(
        domain="circuits",
    )
    soup = BeautifulSoup(
        """
        <h2 id="History">History</h2>
        <p>Some history text.</p>
        <h2 id="Legacy">Legacy</h2>
        <p>Legacy text.</p>
        """,
        "html.parser",
    )

    section = scraper._select_section(soup, "Unknown")  # noqa: SLF001

    assert "Some history text." in section.get_text(" ")
    assert "Legacy text." in section.get_text(" ")


def test_is_lap_record_table_true_when_time_and_driver_present() -> None:
    lap_scraper = LapRecordsTableScraper()
    assert is_lap_record_table(["Time", "Driver", "Vehicle"], lap_scraper) is True


def test_is_lap_record_table_false_when_time_missing() -> None:
    lap_scraper = LapRecordsTableScraper()
    assert is_lap_record_table(["Driver", "Vehicle"], lap_scraper) is False


def test_detect_layout_name_prefers_caption() -> None:
    soup = BeautifulSoup(
        """
        <table class="wikitable">
            <caption>Grand Prix Layout</caption>
            <tr><th>Driver</th><th>Time</th></tr>
        </table>
        """,
        "html.parser",
    )

    table = soup.find("table")
    assert table is not None

    layout = detect_layout_name(table, ["Driver", "Time"])

    assert layout == "Grand Prix Layout"


def test_detect_layout_name_falls_back_to_spanning_header() -> None:
    soup = BeautifulSoup(
        """
        <table class="wikitable">
            <tr><th colspan="3">Short Circuit</th></tr>
            <tr><th>Driver</th><th>Time</th><th>Vehicle</th></tr>
        </table>
        """,
        "html.parser",
    )

    table = soup.find("table")
    assert table is not None

    layout = detect_layout_name(table, ["Driver", "Time", "Vehicle"])

    assert layout == "Short Circuit"
