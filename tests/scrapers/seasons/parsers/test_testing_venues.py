# ruff: noqa: E501, PLR2004
from unittest.mock import MagicMock

from scrapers.domain_parsing_policy import DomainParsingPolicy
from scrapers.domain_parsing_policy import TestingVenuesLayout
from scrapers.parsers.wiki.seasons_wiki_table_element_parser_base.testing_venues import (
    TestingVenuesParser,
)


def policy_with_layout(layout):
    policy = MagicMock(spec=DomainParsingPolicy)
    policy.resolve_testing_venues_layout.return_value = layout
    return policy


def table_parser_returning(records):
    tp = MagicMock()
    tp.parse_table.return_value = records
    return tp


def test_parse_returns_empty_when_layout_is_none() -> None:
    parser = TestingVenuesParser(
        table_parser=table_parser_returning([]),
        policy=policy_with_layout(None),
    )
    result = parser.parse(MagicMock(), season_year=2023)
    assert result == []


def test_parse_calls_parse_2011_for_swapped_layout() -> None:
    records = [{"test": 1, "circuit": {"text": "X"}, "event": "Y"}]
    tp = table_parser_returning(records)
    parser = TestingVenuesParser(
        table_parser=tp,
        policy=policy_with_layout(TestingVenuesLayout.SWAPPED_CIRCUIT_EVENT),
    )
    soup = MagicMock()
    result = parser.parse(soup, season_year=2011)
    assert tp.parse_table.called
    assert isinstance(result, list)


def test_parse_calls_parse_2009_for_standard_layout() -> None:
    records = [
        {"test": 1, "event": "Pre-season", "circuit": {"text": "C"}, "dates": None},
    ]
    tp = table_parser_returning(records)
    parser = TestingVenuesParser(
        table_parser=tp,
        policy=policy_with_layout(TestingVenuesLayout.STANDARD),
    )
    soup = MagicMock()
    result = parser.parse(soup, season_year=2009)
    assert tp.parse_table.called
    assert isinstance(result, list)


def test_parse_2011_swaps_circuit_and_event_fields() -> None:
    records = [
        {"test": 1, "circuit": "CircuitField", "event": {"text": "EventField"}},
    ]
    tp = table_parser_returning(records)
    parser = TestingVenuesParser(
        table_parser=tp,
        policy=policy_with_layout(TestingVenuesLayout.SWAPPED_CIRCUIT_EVENT),
    )
    soup = MagicMock()
    result = parser.parse(soup, season_year=2011)
    # After swap: circuit should have the old event value, event should have old circuit
    assert result[0]["circuit"] == {"text": "EventField"}
    assert result[0]["event"] == "CircuitField"


def test_parse_2009_passes_correct_section_ids() -> None:
    tp = table_parser_returning([])
    parser = TestingVenuesParser(
        table_parser=tp,
        policy=policy_with_layout(TestingVenuesLayout.STANDARD),
    )
    soup = MagicMock()
    parser.parse(soup, season_year=2009)
    call_kwargs = tp.parse_table.call_args
    assert "Testing_venues_and_dates" in call_kwargs.kwargs.get("section_ids", [])
