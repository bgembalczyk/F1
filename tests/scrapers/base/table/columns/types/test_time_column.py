# ruff: noqa: E501, PLR2004
import pytest

from scrapers.base.helpers.value_objects.normalized_time import NormalizedTime
from scrapers.base.table.columns.context import ColumnContext
from scrapers.base.table.columns.types.time import TimeColumn


def ctx(clean_text: str | None) -> ColumnContext:
    return ColumnContext(
        header="Time",
        key="time",
        raw_text=clean_text,
        clean_text=clean_text,
        links=[],
        cell=None,
        base_url="https://en.wikipedia.org",
    )


def test_time_column_empty_returns_none_normalized_time() -> None:
    result = TimeColumn().parse(ctx(""))
    assert result == NormalizedTime(text=None, seconds=None)


def test_time_column_none_returns_none_normalized_time() -> None:
    result = TimeColumn().parse(ctx(None))
    assert result == NormalizedTime(text=None, seconds=None)


def test_time_column_colon_format_parses_seconds() -> None:
    result = TimeColumn().parse(ctx("1:23.456"))
    assert result.text == "1:23.456"
    assert result.seconds is not None
    assert abs(result.seconds - 83.456) < 0.001


def test_time_column_text_with_parenthesis_strips_qualifier() -> None:
    # Line 31: base = text.split("(", 1)[0].strip()
    result = TimeColumn().parse(ctx("1:23.456 (qualifying)"))
    assert result.text == "1:23.456 (qualifying)"
    assert result.seconds is not None
    assert abs(result.seconds - 83.456) < 0.001


def test_time_column_minsec_format_with_min_keyword() -> None:
    # RE_MINSEC branch
    result = TimeColumn().parse(ctx("1min 23.456s"))
    assert result.text is not None
    assert result.seconds is not None
    assert abs(result.seconds - 83.456) < 0.001


def test_time_column_seconds_only_format() -> None:
    # RE_SECONDS branch - "59.876s"
    result = TimeColumn().parse(ctx("59.876s"))
    assert result.text == "59.876s"
    assert result.seconds is not None
    assert abs(result.seconds - 59.876) < 0.001


def test_time_column_plain_seconds_no_suffix() -> None:
    # RE_SECONDS branch - bare number
    result = TimeColumn().parse(ctx("59.876"))
    assert result.text == "59.876"
    assert result.seconds is not None


def test_time_column_unrecognized_format_returns_text_no_seconds() -> None:
    # fallthrough branch
    result = TimeColumn().parse(ctx("N/A"))
    assert result.text == "N/A"
    assert result.seconds is None


@pytest.mark.parametrize("text", ["abc", "?", "retired"])
def test_time_column_various_unparseable_texts(text) -> None:
    result = TimeColumn().parse(ctx(text))
    assert result.seconds is None
    assert result.text is not None
