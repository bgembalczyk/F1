# ruff: noqa: E501, PLR2004
import pytest

from scrapers.domain_parsing_policy import DomainParsingPolicy
from scrapers.domain_parsing_policy import TestingVenuesLayout
from scrapers.parsers.wiki.seasons_wiki_table_element_parser_base import constants


@pytest.fixture()
def policy() -> DomainParsingPolicy:
    return DomainParsingPolicy()


def test_resolve_engine_config_v8_year(policy: DomainParsingPolicy) -> None:
    result = policy.resolve_engine_config(constants.ENGINE_V8_YEAR)
    assert result == {"displacement_l": 2.4, "layout": "V", "cylinders": 8}


def test_resolve_engine_config_v10_year_start(policy: DomainParsingPolicy) -> None:
    result = policy.resolve_engine_config(constants.ENGINE_V10_START_YEAR)
    assert result == {"displacement_l": 3.0, "layout": "V", "cylinders": 10}


def test_resolve_engine_config_v10_year_end(policy: DomainParsingPolicy) -> None:
    result = policy.resolve_engine_config(constants.ENGINE_V10_END_YEAR)
    assert result == {"displacement_l": 3.0, "layout": "V", "cylinders": 10}


def test_resolve_engine_config_v10_mid_range(policy: DomainParsingPolicy) -> None:
    mid = (constants.ENGINE_V10_START_YEAR + constants.ENGINE_V10_END_YEAR) // 2
    result = policy.resolve_engine_config(mid)
    assert result == {"displacement_l": 3.0, "layout": "V", "cylinders": 10}


def test_resolve_engine_config_none_for_other_year(policy: DomainParsingPolicy) -> None:
    assert policy.resolve_engine_config(2023) is None


def test_resolve_engine_config_none_for_none(policy: DomainParsingPolicy) -> None:
    assert policy.resolve_engine_config(None) is None


def test_should_normalize_entry_numbers_before_cutoff(
    policy: DomainParsingPolicy,
) -> None:
    assert (
        policy.should_normalize_entry_numbers(
            constants.PRE_2007_NORMALIZATION_CUTOFF - 1,
        )
        is True
    )


def test_should_normalize_entry_numbers_at_cutoff(policy: DomainParsingPolicy) -> None:
    assert (
        policy.should_normalize_entry_numbers(constants.PRE_2007_NORMALIZATION_CUTOFF)
        is False
    )


def test_should_normalize_entry_numbers_none(policy: DomainParsingPolicy) -> None:
    assert policy.should_normalize_entry_numbers(None) is False


def test_resolve_testing_venues_layout_returns_none_for_unsupported_year(
    policy: DomainParsingPolicy,
) -> None:
    assert policy.resolve_testing_venues_layout(2023) is None
    assert policy.resolve_testing_venues_layout(None) is None


def test_resolve_testing_venues_layout_swapped_for_2011(
    policy: DomainParsingPolicy,
) -> None:
    result = policy.resolve_testing_venues_layout(
        constants.TESTING_VENUES_SWAPPED_COLUMNS_YEAR,
    )
    assert result is TestingVenuesLayout.SWAPPED_CIRCUIT_EVENT


def test_resolve_testing_venues_layout_standard_for_other_testing_years(
    policy: DomainParsingPolicy,
) -> None:
    standard_years = constants.TESTING_VENUES_YEARS - {
        constants.TESTING_VENUES_SWAPPED_COLUMNS_YEAR,
    }
    for year in standard_years:
        result = policy.resolve_testing_venues_layout(year)
        assert result is TestingVenuesLayout.STANDARD
