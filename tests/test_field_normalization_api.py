from __future__ import annotations

import pytest

from models.domain_utils.field_normalization.aliases import expand_alias_variants
from models.domain_utils.field_normalization.links import is_empty_link
from models.domain_utils.field_normalization.links import normalize_link_item
from models.domain_utils.field_normalization.links import normalize_link_items
from models.domain_utils.field_normalization.links import normalize_link_payload
from models.domain_utils.field_normalization.names import add_unique_name
from models.domain_utils.field_normalization.names import normalize_name
from models.domain_utils.field_normalization.stats import extract_driver_stats_row
from models.domain_utils.field_normalization.stats import is_driver_stats_table
from models.domain_utils.field_normalization.stats import normalize_stats_headers


def _validate_link(payload, *, field_name: str):
    if payload is None:
        return {"text": "", "url": None}
    return normalize_link_payload(payload)


def test_normalize_name_and_add_unique_name() -> None:
    seen: set[str] = set()
    names: list[str] = []

    add_unique_name(seen, names, "  Monza  ")
    add_unique_name(seen, names, "monza")  # duplicate regression: case-insensitive
    add_unique_name(seen, names, None)

    assert normalize_name("  Imola ") == "Imola"
    assert normalize_name("   ") is None
    assert names == ["Monza"]


def test_expand_alias_variants_regression_ignores_empty_values() -> None:
    ids, texts = expand_alias_variants(
        {" Career results ", "", "  "},
        text_normalizer=lambda value: value.strip().lower(),
    )

    assert texts == {"career results"}
    assert ids == {"career results", "career_results"}


def test_stats_helpers_support_podiums_and_top_tens() -> None:
    podium_headers = ["Wins", "Podiums", "Poles"]
    top_tens_headers = ["Wins", "Top tens", "Poles"]

    assert normalize_stats_headers(podium_headers) == ["wins", "podiums", "poles"]
    assert is_driver_stats_table(podium_headers, expected_columns=3)
    assert is_driver_stats_table(top_tens_headers, expected_columns=3)

    assert extract_driver_stats_row(["12", "55", "7"], podium_headers) == {
        "wins": 12,
        "podiums": 55,
        "poles": 7,
    }
    assert extract_driver_stats_row(["10", "99", "3"], top_tens_headers) == {
        "wins": 10,
        "top_tens": 99,
        "poles": 3,
    }


def test_extract_driver_stats_row_regression_non_numeric_values_are_skipped() -> None:
    assert extract_driver_stats_row(["x", "4", "y"], ["Wins", "Podiums", "Poles"]) == {
        "podiums": 4,
    }


def test_link_helpers_normalize_and_filter_empty_payloads() -> None:
    assert normalize_link_payload({"text": " Max ", "url": ""}) == {
        "text": "Max",
        "url": None,
    }
    assert is_empty_link({"text": "", "url": None})

    assert normalize_link_item(
        {"text": " Driver ", "url": "https://example.com"},
        field_name="driver",
        validate_payload=_validate_link,
    ) == {"text": "Driver", "url": "https://example.com"}

    assert normalize_link_items(
        [
            {"text": "  Driver  ", "url": ""},
            {"text": "", "url": None},
            "Team",
            "   ",
        ],
        field_name="entries",
        validate_payload=_validate_link,
    ) == [
        {"text": "Driver", "url": None},
        {"text": "Team", "url": None},
    ]


def test_normalize_link_item_rejects_unsupported_type() -> None:
    with pytest.raises(ValueError):
        normalize_link_item(123, field_name="driver", validate_payload=_validate_link)
