# ruff: noqa: E501, PLR2004
import pytest

from scrapers.base.table.columns.context import ColumnContext
from scrapers.races.columns.restart_status import RestartStatusColumn
from scrapers.races.helpers.restart_status import restart_status


def _ctx(clean_text: str | None) -> ColumnContext:
    return ColumnContext(
        header="R",
        key="restart_status",
        raw_text=clean_text,
        clean_text=clean_text,
        links=[],
        cell=None,
        base_url="https://en.wikipedia.org",
    )


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
    result = restart_status(_ctx(text))
    assert result is not None
    assert result["code"] == expected_code
    assert result["description"] == expected_description


def test_restart_status_unknown_code_returns_none_description() -> None:
    result = restart_status(_ctx("X"))
    assert result is not None
    assert result["code"] == "X"
    assert result["description"] is None


def test_restart_status_empty_text_returns_none() -> None:
    assert restart_status(_ctx("")) is None
    assert restart_status(_ctx(None)) is None
    assert restart_status(_ctx("   ")) is None


def test_restart_status_column_delegates_to_helper() -> None:
    col = RestartStatusColumn()
    ctx = _ctx("Y")
    result = col.parse(ctx)
    assert result == {
        "code": "Y",
        "description": "race_was_restarted_over_original_distance",
    }


def test_restart_status_column_empty_returns_none() -> None:
    col = RestartStatusColumn()
    assert col.parse(_ctx("")) is None
