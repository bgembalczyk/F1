# ruff: noqa: E501
from __future__ import annotations

from dataclasses import asdict

import pytest
from bs4 import BeautifulSoup

from models.records.base_factory import RecordFactoryProtocol
from models.records.factories.registry import FACTORY_REGISTRY
from scrapers.base.options import ScraperOptions
from scrapers.base.sections.adapter import SectionAdapter
from scrapers.base.sections.interface import SectionParser
from scrapers.circuits.postprocess.assembler import CircuitRecordAssembler
from scrapers.circuits.postprocess.assembler import CircuitRecordDTO
from scrapers.circuits.sections.layout_history import CircuitLayoutHistorySectionParser
from scrapers.circuits.sections.service import CircuitSectionExtractionService
from scrapers.constructors.postprocess.assembler import ConstructorRecordAssembler
from scrapers.constructors.postprocess.assembler import ConstructorRecordDTO
from scrapers.constructors.sections.history import ConstructorHistorySectionParser
from scrapers.constructors.sections.service import ConstructorSectionExtractionService
from scrapers.drivers.postprocess.assembler import DriverRecordAssembler
from scrapers.drivers.postprocess.assembler import DriverRecordDTO
from scrapers.drivers.sections.career import DriverCareerSectionParser
from scrapers.drivers.sections.results import DriverResultsSectionParser
from scrapers.drivers.sections.service import DriverSectionExtractionService
from scrapers.grands_prix.sections.by_year import GrandPrixByYearSectionParser
from scrapers.seasons.postprocess.assembler import SeasonRecordAssembler
from scrapers.seasons.postprocess.assembler import SeasonRecordSections
from scrapers.seasons.sections.regulation_changes import (
    SeasonRegulationChangesSectionParser,
)
from scrapers.seasons.sections.service import SeasonTextSectionExtractionService

SECTION_RESULT_KEYS = ("section_id", "section_label", "records", "metadata")


def _soup(html: str) -> BeautifulSoup:
    return BeautifulSoup(html, "html.parser")


@pytest.mark.parametrize(
    ("parser", "html"),
    [
        (
            ConstructorHistorySectionParser(),
            '<table class="wikitable"><tr><th>Year</th></tr><tr><td>1950</td></tr></table>',
        ),
        (CircuitLayoutHistorySectionParser(), "<p>First layout</p>"),
        (
            DriverCareerSectionParser(
                parser=DriverResultsSectionParser(
                    options=ScraperOptions(include_urls=False),
                    url="https://example.com/driver",
                ),
            ),
            '<table class="wikitable"><tr><th>Season</th><th>Series</th><th>Position</th></tr><tr><td>2024</td><td>F1</td><td>1</td></tr></table>',
        ),
        (SeasonRegulationChangesSectionParser(), "<ul><li>Rules update</li></ul>"),
        (
            GrandPrixByYearSectionParser(
                url="https://example.com/gp",
                include_urls=False,
                normalize_empty_values=True,
            ),
            '<table class="wikitable"><tr><th>Year</th><th>Driver</th><th>Constructor</th><th>Report</th></tr><tr><td>2024</td><td>Max Verstappen</td><td>Red Bull-Ford</td><td>Race report</td></tr></table>',
        ),
    ],
)
def test_section_parser_contract_for_each_domain_implementation(
    parser: SectionParser,
    html: str,
) -> None:
    result = parser.parse(_soup(html))
    assert tuple(asdict(result).keys()) == SECTION_RESULT_KEYS


@pytest.mark.parametrize(
    ("assembler", "payload", "expected_keys"),
    [
        (
            DriverRecordAssembler(),
            DriverRecordDTO(url="u", infobox={"title": "A"}, career_results=[]),
            {"url", "infobox", "career_results"},
        ),
        (
            ConstructorRecordAssembler(),
            ConstructorRecordDTO(url="u", infoboxes=[], tables=[], sections=[]),
            {"url", "infoboxes", "tables", "sections"},
        ),
        (
            CircuitRecordAssembler(),
            CircuitRecordDTO(url="u", infobox={}, lap_record_rows=[], sections=[]),
            {"url", "infobox", "tables", "sections"},
        ),
        (
            SeasonRecordAssembler(),
            SeasonRecordSections.empty(),
            {
                "entries",
                "free_practice_drivers",
                "calendar",
                "cancelled_rounds",
                "testing_venues_and_dates",
                "results",
                "non_championship_races",
                "scoring_system",
                "drivers_standings",
                "constructors_standings",
                "jim_clark_trophy",
                "colin_chapman_trophy",
                "south_african_formula_one_championship",
                "british_formula_one_championship",
                "regulation_changes",
                "mid_season_changes",
            },
        ),
    ],
)
def test_record_assembler_contract_for_each_domain_implementation(
    assembler: object,
    payload: object,
    expected_keys: set[str],
) -> None:
    if isinstance(assembler, SeasonRecordAssembler):
        record = assembler.assemble(payload)  # type: ignore[arg-type]
    else:
        record = assembler.assemble(payload=payload)  # type: ignore[call-arg]
    assert isinstance(record, dict)
    assert expected_keys.issubset(record)


@pytest.mark.parametrize(
    ("service", "html"),
    [
        (
            DriverSectionExtractionService(
                adapter=SectionAdapter(),
                options=ScraperOptions(include_urls=True),
                url="https://example.com/driver",
            ),
            "<h2 id='Non-championship_races'>Races</h2><table class='wikitable'><tr><th>Year</th></tr><tr><td>1950</td></tr></table>",
        ),
        (
            ConstructorSectionExtractionService(
                adapter=SectionAdapter(),
                options=ScraperOptions(include_urls=True),
                url="https://example.com/constructor",
            ),
            "<h2 id='History'>History</h2><table class='wikitable'><tr><th>Year</th></tr><tr><td>1950</td></tr></table>",
        ),
        (
            CircuitSectionExtractionService(
                adapter=SectionAdapter(),
                options=ScraperOptions(include_urls=True),
                url="https://example.com/circuit",
            ),
            "<h2 id='Layout_history'>Layout</h2><p>first</p>",
        ),
        (
            SeasonTextSectionExtractionService(adapter=SectionAdapter()),
            "<h2 id='Regulation_changes'>Regulation changes</h2><ul><li>New points</li></ul>",
        ),
    ],
)
def test_section_service_contract_for_each_domain_implementation(
    service: object,
    html: str,
) -> None:
    result = service.extract(_soup(html))
    assert isinstance(result, (list, dict))
    assert result


@pytest.mark.parametrize("record_type", sorted(FACTORY_REGISTRY))
def test_record_factory_contract_for_each_registered_implementation(
    record_type: str,
) -> None:
    factory = FACTORY_REGISTRY[record_type]
    assert isinstance(factory, RecordFactoryProtocol)
    assert factory.record_type == record_type
    assert callable(factory.build)
