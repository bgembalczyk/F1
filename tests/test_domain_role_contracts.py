# ruff: noqa: E501
from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest
from bs4 import BeautifulSoup

from models.records.base_factory import RecordFactoryProtocol
from models.records.factories import registry as factory_registry_module
from scrapers.base.domain_entrypoint import get_domain_entrypoint_scraper_metadata
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

SECTION_RESULT_KEYS = ("section_id", "section_label", "records", "metadata")
PROJECT_ROOT = Path(__file__).resolve().parents[1]
FACTORY_REGISTRY = getattr(
    factory_registry_module,
    "FACTORY_REGISTRY",
    factory_registry_module.build_factory_registry(),
)

DOMAIN_CONTRACT_MATRIX: dict[str, dict[str, Any]] = {
    "drivers": {
        "assembler": DriverRecordAssembler(),
        "assembler_payload": DriverRecordDTO(
            url="u",
            infobox={"title": "A"},
            career_results=[],
        ),
        "assembler_expected_keys": {"url", "infobox", "career_results"},
        "section_service": DriverSectionExtractionService(
            adapter=SectionAdapter(),
            options=ScraperOptions(include_urls=True),
            url="https://example.com/driver",
        ),
        "section_html": "<h2 id='Non-championship_races'>Races</h2><table class='wikitable'><tr><th>Year</th></tr><tr><td>1950</td></tr></table>",
        "record_factory_type": "driver",
        "required_protocols": (
            "record_assembler",
            "section_extractor",
            "record_factory",
        ),
    },
    "constructors": {
        "assembler": ConstructorRecordAssembler(),
        "assembler_payload": ConstructorRecordDTO(
            url="u",
            infoboxes=[],
            tables=[],
            sections=[],
        ),
        "assembler_expected_keys": {"url", "infoboxes", "tables", "sections"},
        "section_service": ConstructorSectionExtractionService(
            adapter=SectionAdapter(),
            options=ScraperOptions(include_urls=True),
            url="https://example.com/constructor",
        ),
        "section_html": "<h2 id='History'>History</h2><table class='wikitable'><tr><th>Year</th></tr><tr><td>1950</td></tr></table>",
        "record_factory_type": "constructor",
        "required_protocols": (
            "record_assembler",
            "section_extractor",
            "record_factory",
        ),
    },
    "circuits": {
        "assembler": CircuitRecordAssembler(),
        "assembler_payload": CircuitRecordDTO(
            url="u",
            infobox={},
            lap_record_rows=[],
            sections=[],
        ),
        "assembler_expected_keys": {"url", "infobox", "tables", "sections"},
        "section_service": CircuitSectionExtractionService(
            adapter=SectionAdapter(),
            options=ScraperOptions(include_urls=True),
            url="https://example.com/circuit",
        ),
        "section_html": "<h2 id='Layout_history'>Layout</h2><p>first</p>",
        "record_factory_type": "circuit",
        "required_protocols": (
            "record_assembler",
            "section_extractor",
            "record_factory",
        ),
    },
    "seasons": {
        "assembler": SeasonRecordAssembler(),
        "assembler_payload": SeasonRecordSections.empty(),
        "assembler_expected_keys": {
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
        "section_service": SeasonTextSectionExtractionService(adapter=SectionAdapter()),
        "section_html": "<h2 id='Regulation_changes'>Regulation changes</h2><ul><li>New points</li></ul>",
        "record_factory_type": "season",
        "required_protocols": (
            "record_assembler",
            "section_extractor",
            "record_factory",
        ),
    },
}


def _soup(html: str) -> BeautifulSoup:
    return BeautifulSoup(html, "html.parser")


def _single_article_domains_requiring_contract_matrix() -> set[str]:
    scrapers_dir = PROJECT_ROOT / "scrapers"
    entrypoint_domains = set(get_domain_entrypoint_scraper_metadata())
    return {
        domain_dir.name
        for domain_dir in scrapers_dir.iterdir()
        if domain_dir.is_dir()
        and domain_dir.name in entrypoint_domains
        and (domain_dir / "sections" / "service.py").exists()
        and (domain_dir / "postprocess" / "assembler.py").exists()
    }


def test_domain_contract_matrix_covers_all_single_article_domains() -> None:
    expected_domains = _single_article_domains_requiring_contract_matrix()
    assert set(DOMAIN_CONTRACT_MATRIX) == expected_domains


@pytest.mark.parametrize("domain", sorted(DOMAIN_CONTRACT_MATRIX))
def test_domain_contract_matrix_uses_registered_domain_names(domain: str) -> None:
    entrypoint_domains = set(get_domain_entrypoint_scraper_metadata())
    assert domain in entrypoint_domains


@pytest.mark.parametrize("domain", sorted(DOMAIN_CONTRACT_MATRIX))
def test_record_assembler_contract_for_domain(domain: str) -> None:
    contract = DOMAIN_CONTRACT_MATRIX[domain]
    assembler = contract["assembler"]
    payload = contract["assembler_payload"]

    if isinstance(assembler, SeasonRecordAssembler):
        record = assembler.assemble(payload)  # type: ignore[arg-type]
    else:
        record = assembler.assemble(payload=payload)  # type: ignore[call-arg]

    assert isinstance(record, dict)
    assert contract["assembler_expected_keys"].issubset(record)


@pytest.mark.parametrize("domain", sorted(DOMAIN_CONTRACT_MATRIX))
def test_section_service_contract_for_domain(domain: str) -> None:
    contract = DOMAIN_CONTRACT_MATRIX[domain]
    service = contract["section_service"]
    result = service.extract(_soup(contract["section_html"]))

    assert isinstance(result, list | dict)
    assert result


@pytest.mark.parametrize("domain", sorted(DOMAIN_CONTRACT_MATRIX))
def test_domain_required_protocols_contract(domain: str) -> None:
    contract = DOMAIN_CONTRACT_MATRIX[domain]
    factory = FACTORY_REGISTRY[contract["record_factory_type"]]

    assert set(contract["required_protocols"]) == {
        "record_assembler",
        "section_extractor",
        "record_factory",
    }
    assert callable(getattr(contract["assembler"], "assemble", None))
    assert callable(getattr(contract["section_service"], "extract", None))
    assert isinstance(factory, RecordFactoryProtocol)
    assert factory.record_type == contract["record_factory_type"]
    assert callable(factory.build)


@pytest.mark.parametrize("record_type", sorted(FACTORY_REGISTRY))
def test_record_factory_contract_for_each_registered_implementation(
    record_type: str,
) -> None:
    factory = FACTORY_REGISTRY[record_type]
    assert isinstance(factory, RecordFactoryProtocol)
    assert factory.record_type == record_type
    assert callable(factory.build)
