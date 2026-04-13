# ruff: noqa: E501, PLR2004
import pytest

from scrapers.columns.types.restart_status import RestartStatusColumn
from tests.scrapers.base.table.columns.types.helpers import ctx_restart


@pytest.mark.parametrize(
    ("text", "expected_code", "expected_description"),
    [
        ("N", "N", "race_was_not_restarted"),
        ("Y", "Y", "race_was_restarted_over_original_distance"),
        ("R", "R", "race_was_resumed_to_complete_original_distance"),
        (
            "S",
            "S",
            "race_was_restarted_or_resumed_without_completing_original_distance",
        ),
        ("n", "N", "race_was_not_restarted"),
        ("y", "Y", "race_was_restarted_over_original_distance"),
    ],
)
def test_restart_status_known_codes(text, expected_code, expected_description) -> None:
    col = RestartStatusColumn()
    result = col.parse(ctx_restart(text))
    assert result is not None
    assert result["code"] == expected_code
    assert result["description"] == expected_description


def test_restart_status_unknown_code_returns_none_description() -> None:
    col = RestartStatusColumn()
    result = col.parse(ctx_restart("X"))
    assert result is not None
    assert result["code"] == "X"
    assert result["description"] is None


def test_restart_status_empty_text_returns_none() -> None:
    col = RestartStatusColumn()
    assert col.parse(ctx_restart("")) is None
    assert col.parse(ctx_restart(None)) is None
    assert col.parse(ctx_restart("   ")) is None


def test_restart_status_column() -> None:
    col = RestartStatusColumn()
    context = ctx_restart("Y")
    result = col.parse(context)
    assert result == {
        "code": "Y",
        "description": "race_was_restarted_over_original_distance",
    }


def test_restart_status_column_empty_returns_none() -> None:
    col = RestartStatusColumn()
    assert col.parse(ctx_restart("")) is None
