# ruff: noqa: E501
from __future__ import annotations

from typing import TYPE_CHECKING
from typing import Any

import pytest
from bs4 import BeautifulSoup

from models.records.base_factory import RecordFactoryProtocol
from models.records.factories.registry import FACTORY_REGISTRY
from scrapers.base.options import ScraperOptions
from scrapers.base.sections.adapter import SectionAdapter
from scrapers.circuits.postprocess.assembler import CircuitRecordAssembler
from scrapers.circuits.postprocess.assembler import CircuitRecordDTO
from scrapers.circuits.sections.service import CircuitSectionExtractionService
from scrapers.constructors.postprocess.assembler import ConstructorRecordAssembler
from scrapers.constructors.postprocess.assembler import ConstructorRecordDTO
from scrapers.constructors.sections.service import ConstructorSectionExtractionService
from scrapers.drivers.postprocess.assembler import DriverRecordAssembler
from scrapers.drivers.postprocess.assembler import DriverRecordDTO
from scrapers.drivers.sections.service import DriverSectionExtractionService
from scrapers.seasons.postprocess.assembler import SeasonRecordAssembler
from scrapers.seasons.postprocess.assembler import SeasonRecordSections
from scrapers.seasons.sections.service import SeasonTextSectionExtractionService

if TYPE_CHECKING:
    from scrapers.base.contracts import RecordAssemblerProtocol
    from scrapers.base.contracts import SectionExtractionServiceProtocol

SECTION_RESULT_KEYS = ("section_id", "section_label", "records", "metadata")


def _soup(html: str) -> BeautifulSoup:
    return BeautifulSoup(html, "html.parser")


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
    assembler: RecordAssemblerProtocol[
        DriverRecordDTO
        | ConstructorRecordDTO
        | CircuitRecordDTO
        | SeasonRecordSections
    ],
    payload: DriverRecordDTO | ConstructorRecordDTO | CircuitRecordDTO | SeasonRecordSections,
    expected_keys: set[str],
) -> None:
    record = assembler.assemble(payload)
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
    service: SectionExtractionServiceProtocol[list[dict[str, Any]] | dict[str, list[dict[str, Any]]]],
    html: str,
) -> None:
    result = service.extract(_soup(html))
    assert isinstance(result, list | dict)
    assert result


@pytest.mark.parametrize("record_type", sorted(FACTORY_REGISTRY))
def test_record_factory_contract_for_each_registered_implementation(
    record_type: str,
) -> None:
    factory = FACTORY_REGISTRY[record_type]
    assert isinstance(factory, RecordFactoryProtocol)
    assert factory.record_type == record_type
    assert callable(factory.build)
