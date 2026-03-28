# ruff: noqa: E501, PLR2004
from bs4 import BeautifulSoup

from scrapers.base.options import ScraperOptions
from scrapers.base.sections.adapter import SectionAdapter
from scrapers.base.sections.adapter import SectionAdapterEntry
from scrapers.base.sections.constants import DOMAIN_CRITICAL_SECTIONS
from scrapers.circuits.sections.events import CircuitEventsSectionParser
from scrapers.circuits.sections.lap_records import CircuitLapRecordsSectionParser
from scrapers.circuits.sections.layout_history import CircuitLayoutHistorySectionParser
from scrapers.constructors.single_scraper import SingleConstructorScraper
from scrapers.drivers.single_scraper import SingleDriverScraper
from scrapers.grands_prix.single_scraper import F1SingleGrandPrixScraper
from scrapers.seasons.single_scraper import SingleSeasonScraper


def test_constructor_sections_are_parsed_through_section_adapter() -> None:
    scraper = SingleConstructorScraper()
    scraper.url = "https://example.com/constructor"
    soup = BeautifulSoup(
        """
        <h2 id="History">History</h2><table class="wikitable"><tr><th>Year</th></tr><tr><td>1950</td></tr></table>
        <h2 id="Formula_One/World_Championship_results">Championship results</h2>
        <table class="wikitable"><tr><th>Season</th></tr><tr><td>1950</td></tr></table>
        <h2 id="Complete_World_Championship_results">Complete</h2>
        <table class="wikitable"><tr><th>Year</th></tr><tr><td>1950</td></tr></table>
        """,
        "html.parser",
    )

    result = scraper._parse_soup(soup)[0]  # noqa: SLF001

    assert len(result["sections"]) == 3
    assert {section["section_id"] for section in result["sections"]} == {
        "history",
        "championship_results",
        "complete_formula_one_results",
    }
    assert all(
        set(section) == {"section_id", "section_label", "records", "metadata"}
        for section in result["sections"]
    )


def test_circuit_sections_are_parsed_through_section_adapter() -> None:
    class _CircuitSectionsHarness(SectionAdapter):
        pass

    scraper = _CircuitSectionsHarness()
    soup = BeautifulSoup(
        """
        <div id="mw-normal-catlinks"><a href="/wiki/Category:Formula_One_circuits">Formula One circuits</a></div>
        <h2 id="History">History</h2><p>First layout</p>
        <h2 id="Formula_One_lap_records">Lap records</h2>
        <table class="wikitable"><tr><th>Driver</th><th>Time</th></tr><tr><td>A. Senna</td><td>1:20.000</td></tr></table>
        <h2 id="Races">Races</h2>
        <table class="wikitable"><tr><th>Series</th></tr><tr><td>Formula One</td></tr></table>
        """,
        "html.parser",
    )

    sections = scraper.parse_section_dicts(
        soup=soup,
        domain="circuits",
        entries=[
            SectionAdapterEntry(
                section_id="layout_history",
                aliases=("Layout_history", "History"),
                parser=CircuitLayoutHistorySectionParser(),
            ),
            SectionAdapterEntry(
                section_id="lap_records",
                aliases=("Lap_records", "Formula_One_lap_records"),
                parser=CircuitLapRecordsSectionParser(
                    options=ScraperOptions(include_urls=True),
                    url="https://example.com/circuit",
                ),
            ),
            SectionAdapterEntry(
                section_id="events",
                aliases=("Events", "Races"),
                parser=CircuitEventsSectionParser(),
            ),
        ],
    )

    assert {section["section_id"] for section in sections} == {
        "layout_history",
        "lap_records",
        "events",
    }
    assert all(
        set(section) == {"section_id", "section_label", "records", "metadata"}
        for section in sections
    )


def test_driver_sections_include_non_championship_alias() -> None:
    scraper = SingleDriverScraper(options=ScraperOptions(include_urls=True))
    scraper.url = "https://example.com/driver"
    soup = BeautifulSoup(
        """
        <h2 id="Non-championship_races">Non champ</h2>
        <table class="wikitable"><tr><th>Year</th></tr><tr><td>1950</td></tr></table>
        """,
        "html.parser",
    )

    records = scraper._build_sections_payload(soup)  # noqa: SLF001

    assert records
    assert all(record["section_id"] == "Non-championship" for record in records)


def test_single_season_separates_text_sections() -> None:
    scraper = SingleSeasonScraper(
        options=ScraperOptions(include_urls=True),
        season_year=2024,
    )
    scraper.url = "https://example.com/2024_Formula_One_World_Championship"
    scraper._table_parser.update_url(scraper.url)  # noqa: SLF001
    soup = BeautifulSoup(
        """
        <h2 id="Regulation_changes">Regulation changes</h2>
        <ul><li>Point system update</li></ul>
        <h2 id="Mid-season_changes">Mid-season changes</h2>
        <ul><li>Driver transfer</li></ul>
        """,
        "html.parser",
    )

    result = scraper._parse_soup(soup)[0]  # noqa: SLF001

    assert result["regulation_changes"] == [{"text": "Point system update"}]
    assert result["mid_season_changes"] == [{"text": "Driver transfer"}]


def test_grand_prix_by_year_uses_domain_critical_alias_fallback() -> None:
    scraper = F1SingleGrandPrixScraper(options=ScraperOptions(include_urls=True))
    scraper.url = "https://example.com/gp"
    soup = BeautifulSoup(
        """
        <div id="mw-normal-catlinks"><a href="/wiki/Category:Formula_One_Grand_Prix">Formula One Grand Prix</a></div>
        <h2 id="Winners">Winners</h2>
        <table class="wikitable">
          <tr><th>Year</th><th>Driver</th><th>Constructor</th><th>Report</th></tr>
          <tr><td>2024</td><td><a href="/wiki/Max_Verstappen">Max Verstappen</a></td>
              <td>Red Bull-Ford</td><td>Race report</td></tr>
        </table>
        """,
        "html.parser",
    )

    result = scraper.parse(soup)

    assert result[0]["section_id"] == "Winners"
    assert result[0]["by_year"]


def test_each_critical_section_has_alias_fallback() -> None:
    required_domains = {"drivers", "constructors", "circuits", "seasons", "grands_prix"}
    assert required_domains.issubset(DOMAIN_CRITICAL_SECTIONS.keys())

    for domain in required_domains:
        sections = DOMAIN_CRITICAL_SECTIONS[domain]
        assert sections, f"Missing critical sections for domain={domain}"
        for section in sections:
            assert section.alternative_section_ids, f"Critical section without aliases: domain={domain} section={section.section_id}"
