from __future__ import annotations

from dataclasses import asdict

from bs4 import BeautifulSoup

from scrapers.base.sections.interface import SectionParseResult
from scrapers.base.sections.table_section_parser import TableSectionParser
from scrapers.base.table.config import TableScraperConfig
from tests._section_parser_fixture_pattern import SectionContractFixture
from tests._section_parser_fixture_pattern import assert_section_contract_template

CONTRACT_CASES = ("section_id", "section_label", "records", "metadata")


def test_section_parse_result_dataclass_contract() -> None:
    result = SectionParseResult(
        section_id="Results",
        section_label="Results",
        records=[{"year": 2024}],
        metadata={"source": "unit-test"},
    )

    payload = asdict(result)

    assert tuple(payload.keys()) == CONTRACT_CASES
    assert isinstance(result.section_id, str)
    assert isinstance(result.section_label, str)
    assert isinstance(result.records, list)
    assert isinstance(result.metadata, dict)


def test_table_section_parser_returns_section_parse_result_contract() -> None:
    html = """
    <div>
      <table class="wikitable">
        <tr><th>Year</th><th>Champion</th></tr>
        <tr><td>2024</td><td>Max Verstappen</td></tr>
      </table>
    </div>
    """
    parser = TableSectionParser(
        config=TableScraperConfig(
            url="https://example.test/results",
            expected_headers=("year", "champion"),
            column_map={"year": "year", "champion": "champion"},
        ),
        section_id="results",
        section_label="Results",
        domain="constructors",
        include_urls=False,
        normalize_empty_values=True,
    )

    result = parser.parse(BeautifulSoup(html, "html.parser"))

    assert isinstance(result, SectionParseResult)
    assert result.section_id == "results"
    assert result.section_label == "Results"
    fixture = SectionContractFixture(
        html=html,
        expected_records=[{"year": "2024", "champion": "Max Verstappen"}],
        expected_metadata={"parser": "TableSectionParser", "domain": "constructors"},
    )
    assert_section_contract_template(result, fixture)
