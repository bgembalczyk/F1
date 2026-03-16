from __future__ import annotations

from pathlib import Path

from tests._section_parser_fixture_pattern import CONTRACT_COVERED_SECTION_MODULES
from tests._section_parser_fixture_pattern import SECTION_MODULES_REQUIRING_DOD
from tests._section_parser_fixture_pattern import SNAPSHOT_CASES_BY_DOMAIN
from tests._section_parser_fixture_pattern import SNAPSHOT_COVERED_SECTION_MODULES
from tests.test_section_parser_contract import CONTRACT_CASES
from tests.test_section_parser_regressions import ALIAS_DOMAINS

REQUIRED_DOMAINS = {"drivers", "constructors", "circuits", "seasons", "grands_prix"}


def test_ci_meta_requires_snapshot_matrix_for_every_domain() -> None:
    assert REQUIRED_DOMAINS.issubset(SNAPSHOT_CASES_BY_DOMAIN)
    for domain in REQUIRED_DOMAINS:
        variants = {fixture.variant for fixture in SNAPSHOT_CASES_BY_DOMAIN[domain]}
        assert variants == {"minimal", "edge"}


def test_ci_meta_requires_section_parse_result_contract_suite() -> None:
    assert CONTRACT_CASES == ("section_id", "section_label", "records", "metadata")


def test_ci_meta_requires_alias_coverage_for_new_parser_domains() -> None:
    assert {"constructors", "circuits", "seasons"}.issubset(set(ALIAS_DOMAINS))


def test_ci_meta_requires_snapshot_and_contract_for_all_section_modules() -> None:
    assert SNAPSHOT_COVERED_SECTION_MODULES == SECTION_MODULES_REQUIRING_DOD
    assert CONTRACT_COVERED_SECTION_MODULES == SECTION_MODULES_REQUIRING_DOD

def test_ci_meta_requires_sections_boundary_regression_suite() -> None:
    boundary_test_file = Path("tests/test_section_architecture_boundaries.py")
    source = boundary_test_file.read_text(encoding="utf-8")

    assert "test_sections_modules_do_not_import_single_scraper" in source
    assert (
        "test_single_scraper_can_depend_on_sections_without_reverse_dependency"
        in source
    )
