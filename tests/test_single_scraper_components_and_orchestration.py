from __future__ import annotations

from bs4 import BeautifulSoup

from scrapers.base.options import ScraperOptions
from scrapers.circuits.infobox.service import CircuitInfoboxExtractionService
from scrapers.circuits.postprocess.assembler import CircuitRecordAssembler
from scrapers.constructors.infobox.service import ConstructorInfoboxExtractionService
from scrapers.constructors.postprocess.assembler import ConstructorRecordAssembler
from scrapers.constructors.sections.service import ConstructorSectionExtractionService
from scrapers.constructors.single_scraper import SingleConstructorScraper
from scrapers.drivers.infobox.service import DriverInfoboxExtractionService
from scrapers.drivers.postprocess.assembler import DriverRecordAssembler
from scrapers.drivers.sections.service import DriverSectionExtractionService
from scrapers.drivers.single_scraper import SingleDriverScraper
from scrapers.seasons.postprocess.assembler import SeasonRecordAssembler
from scrapers.seasons.sections.service import SeasonTextSectionExtractionService
from scrapers.seasons.single_scraper import SingleSeasonScraper


def _soup(html: str) -> BeautifulSoup:
    return BeautifulSoup(html, "html.parser")


def test_driver_infobox_service_returns_empty_without_infobox() -> None:
    service = DriverInfoboxExtractionService(
        include_urls=True,
        debug_dir=None,
        run_id=None,
    )
    assert service.extract(_soup("<div>nope</div>"), url="https://example.com") == {}


def test_driver_sections_service_extracts_alias_section_id() -> None:
    scraper = SingleDriverScraper(options=ScraperOptions(include_urls=True))
    service = DriverSectionExtractionService(
        adapter=scraper,
        options=ScraperOptions(include_urls=True),
        url="https://example.com/driver",
    )
    records = service.extract(
        _soup(
            """
            <h2 id='Non-championship_races'>Non champ</h2>
            <table class='wikitable'><tr><th>Year</th></tr><tr><td>1950</td></tr></table>
            """,
        ),
    )
    assert records
    assert all(r["section_id"] == "Non-championship" for r in records)


def test_driver_assembler_builds_record_shape() -> None:
    record = DriverRecordAssembler().assemble(
        url="u",
        infobox={"title": "A"},
        career_results=[{"year": "2024"}],
    )
    assert record == {
        "url": "u",
        "infobox": {"title": "A"},
        "career_results": [{"year": "2024"}],
    }


def test_constructor_component_services_and_assembler() -> None:
    soup = _soup(
        """
        <table class='infobox'><caption>Team</caption></table>
        <h2 id='History'>History</h2><table class='wikitable'><tr><th>Year</th></tr><tr><td>1950</td></tr></table>
        """,
    )
    scraper = SingleConstructorScraper()
    infoboxes = ConstructorInfoboxExtractionService().extract(soup)
    sections = ConstructorSectionExtractionService(adapter=scraper).extract(soup)
    record = ConstructorRecordAssembler().assemble(
        url="x",
        infoboxes=infoboxes,
        tables=[],
        sections=sections,
    )
    assert record["url"] == "x"
    assert record["infoboxes"][0]["title"] == "Team"
    assert record["sections"][0]["section_id"] == "history"


def test_circuit_component_services_and_assembler() -> None:
    soup = _soup("<table class='infobox'><caption>Track</caption></table>")
    infobox = CircuitInfoboxExtractionService(
        include_urls=True,
        debug_dir=None,
    ).extract(soup, url="https://example.com/circuit")
    record = CircuitRecordAssembler().assemble(
        url="u",
        infobox=infobox,
        tables=[],
        sections=[],
    )
    assert record["infobox"]["title"] == "Track"


def test_season_text_sections_service_and_assembler() -> None:
    scraper = SingleSeasonScraper(
        options=ScraperOptions(include_urls=True),
        season_year=2024,
    )
    text_records = SeasonTextSectionExtractionService(adapter=scraper).extract(
        _soup(
            """
            <h2 id='Regulation_changes'>Regulation changes</h2>
            <ul><li>New point format</li></ul>
            """,
        ),
    )
    record = SeasonRecordAssembler().assemble(
        entries=[],
        free_practice_drivers=[],
        calendar=[],
        cancelled_rounds=[],
        testing_venues_and_dates=[],
        results=[],
        non_championship_races=[],
        scoring_system=[],
        drivers_standings=[],
        constructors_standings=[],
        jim_clark_trophy=[],
        colin_chapman_trophy=[],
        south_african_formula_one_championship=[],
        british_formula_one_championship=[],
        regulation_changes=text_records.get("Regulation_changes", []),
        mid_season_changes=[],
    )
    assert record["regulation_changes"] == [{"text": "New point format"}]


def test_orchestration_integration_single_driver_uses_injected_dependencies() -> None:
    class _InfoboxStub:
        def extract(self, _soup: BeautifulSoup, *, url: str):
            return {"url": url, "from": "infobox"}

    class _SectionsStub:
        def __init__(self, _options: ScraperOptions, _url: str) -> None:
            pass

        def extract(self, _soup: BeautifulSoup):
            return [{"section_id": "Career_results", "section": "Career"}]

    scraper = SingleDriverScraper(
        options=ScraperOptions(include_urls=True),
        infobox_service=_InfoboxStub(),
        sections_service_factory=lambda options, url: _SectionsStub(options, url),
        assembler=DriverRecordAssembler(),
    )
    scraper.url = "https://example.com/driver"
    result = scraper._parse_soup(_soup("<html></html>"))[0]  # noqa: SLF001

    assert result["infobox"]["from"] == "infobox"
    assert result["career_results"][0]["section"] == "Career"
