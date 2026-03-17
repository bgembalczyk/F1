from __future__ import annotations

from bs4 import BeautifulSoup

from scrapers.base.options import ScraperOptions
from scrapers.drivers.sections.driver_results_schema_factory import (
    DriverResultsSchemaFactory,
)
from scrapers.drivers.sections.driver_results_table_classifier import (
    DriverResultsTableClassifier,
)
from scrapers.drivers.sections.results import DriverResultsSectionParser


def test_driver_results_table_classifier_contract() -> None:
    classifier = DriverResultsTableClassifier()

    assert (
        classifier.classify(["Season", "Series", "Position", "Team", "Car"])
        == "career_highlights"
    )
    assert classifier.classify(["Season", "Series", "Position"]) == "career_summary"
    assert classifier.classify(["Year", "Team", "Pos."]) == "complete_results"
    assert classifier.classify(["Foo", "Bar"]) is None


def test_driver_results_schema_factory_contract_for_complete_results_rounds() -> None:
    factory = DriverResultsSchemaFactory(unknown_value="unknown")

    schema = factory.build(
        table_type="complete_results",
        headers=["Year", "Team", "1", "2"],
    )

    headers = [spec.header for spec in schema.columns]
    assert "Year" in headers
    assert "Team" in headers
    assert "1" in headers
    assert "2" in headers


def test_driver_results_section_parser_orchestration_contract() -> None:
    parser = DriverResultsSectionParser(
        options=ScraperOptions(include_urls=False),
        url="https://example.com/driver",
    )
    html = """
    <table class="wikitable">
      <tr><th>Season</th><th>Series</th><th>Position</th></tr>
      <tr><td>2024</td><td>Formula One</td><td>1st</td></tr>
    </table>
    <table class="wikitable">
      <tr><th>Year</th><th>Team</th><th>Pos.</th></tr>
      <tr><td>2024</td><td>Red Bull</td><td>1st</td></tr>
    </table>
    """

    result = parser.parse(BeautifulSoup(html, "html.parser"))

    assert [record["table_type"] for record in result.records] == [
        "career_summary",
        "complete_results",
    ]
    assert result.records[0]["rows"]
    assert result.records[1]["rows"]
