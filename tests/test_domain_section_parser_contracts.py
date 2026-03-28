# ruff: noqa: E501
from __future__ import annotations

from dataclasses import asdict

from bs4 import BeautifulSoup

from scrapers.base.options import ScraperOptions
from scrapers.circuits.sections.layout_history import CircuitLayoutHistorySectionParser
from scrapers.constructors.sections.history import ConstructorHistorySectionParser
from scrapers.drivers.sections.career import DriverCareerSectionParser
from scrapers.drivers.sections.results import DriverResultsSectionParser
from scrapers.grands_prix.sections.by_year import GrandPrixByYearSectionParser
from scrapers.seasons.sections.regulation_changes import (
    SeasonRegulationChangesSectionParser,
)

CONTRACT_KEYS = ("section_id", "section_label", "records", "metadata")


def test_constructor_section_parser_contract() -> None:
    parser = ConstructorHistorySectionParser()
    result = parser.parse(
        BeautifulSoup(
            '<table class="wikitable"><tr><th>Year</th></tr><tr><td>1950</td></tr></table>',
            "html.parser",
        ),
    )
    assert tuple(asdict(result).keys()) == CONTRACT_KEYS


def test_circuit_section_parser_contract() -> None:
    parser = CircuitLayoutHistorySectionParser()
    result = parser.parse(BeautifulSoup("<p>First layout</p>", "html.parser"))
    assert tuple(asdict(result).keys()) == CONTRACT_KEYS


def test_driver_section_parser_contract() -> None:
    raw = DriverResultsSectionParser(
        options=ScraperOptions(include_urls=False),
        url="https://example.com/driver",
    )
    parser = DriverCareerSectionParser(parser=raw)
    html = '<table class="wikitable"><tr><th>Season</th><th>Series</th><th>Position</th></tr><tr><td>2024</td><td>F1</td><td>1</td></tr></table>'
    result = parser.parse(BeautifulSoup(html, "html.parser"))
    assert tuple(asdict(result).keys()) == CONTRACT_KEYS


def test_season_section_parser_contract() -> None:
    parser = SeasonRegulationChangesSectionParser()
    result = parser.parse(
        BeautifulSoup("<ul><li>Rules update</li></ul>", "html.parser"),
    )
    assert tuple(asdict(result).keys()) == CONTRACT_KEYS


def test_grand_prix_section_parser_contract() -> None:
    parser = GrandPrixByYearSectionParser(
        url="https://example.com/gp",
        include_urls=False,
        normalize_empty_values=True,
    )
    html = """<table class="wikitable">
      <tr><th>Year</th><th>Driver</th><th>Constructor</th><th>Report</th></tr>
      <tr><td>2024</td><td>Max Verstappen</td><td>Red Bull-Ford</td><td>Race report</td></tr>
    </table>"""
    result = parser.parse(BeautifulSoup(html, "html.parser"))
    assert tuple(asdict(result).keys()) == CONTRACT_KEYS
