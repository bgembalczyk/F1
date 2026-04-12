# ruff: noqa: E501, PLR2004
from scrapers.base.table.columns.context import ColumnContext
from scrapers.columns.types.multi.multi import MultiColumn
from scrapers.columns.types.text import TextColumn
from scrapers.base.table.sentinels import SKIP_SENTINEL


def context(clean_text: str | None, raw_text: str | None = None) -> ColumnContext:
    return ColumnContext(
        header="Multi",
        key="multi",
        raw_text=raw_text or clean_text,
        clean_text=clean_text,
        links=[],
        cell=None,
        base_url="https://en.wikipedia.org",
        skip_sentinel=SKIP_SENTINEL,
    )


def test_multi_column_parse_returns_dict_with_subcolumn_results() -> None:
    col = MultiColumn({"name": TextColumn(), "count": TextColumn()})
    ctx = context("hello")
    result = col.parse(ctx)
    assert isinstance(result, dict)
    assert "name" in result
    assert result["name"] == "hello"
    assert result["count"] == "hello"


def test_multi_column_parse_empty_text() -> None:
    col = MultiColumn({"name": TextColumn()})
    ctx = context("")
    result = col.parse(ctx)
    assert isinstance(result, dict)


def test_multi_column_parse_skip_sentinel_excluded() -> None:
    from scrapers.columns.types.skip import SkipColumn

    col = MultiColumn({"skip_key": SkipColumn(), "name": TextColumn()})
    ctx = context("hello")
    result = col.parse(ctx)
    assert "skip_key" not in result
    assert result["name"] == "hello"


def test_multi_column_parse_multiple_subcolumns() -> None:
    col = MultiColumn({"a": TextColumn(), "b": TextColumn(), "c": TextColumn()})
    ctx = context("value")
    result = col.parse(ctx)
    assert result == {"a": "value", "b": "value", "c": "value"}


def test_multi_column_apply_writes_to_record() -> None:
    col = MultiColumn({"name": TextColumn()})
    ctx = context("test_val")
    record: dict = {}
    col.apply(ctx, record)
    assert record["name"] == "test_val"
