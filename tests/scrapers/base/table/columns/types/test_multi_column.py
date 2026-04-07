# ruff: noqa: E501, PLR2004
from scrapers.base.table.columns.context import ColumnContext
from scrapers.base.table.columns.types.multi import MultiColumn
from scrapers.base.table.columns.types.text import TextColumn
from scrapers.base.table.sentinels import SKIP_SENTINEL


def _ctx(clean_text: str | None, raw_text: str | None = None) -> ColumnContext:
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
    ctx = _ctx("hello")
    result = col.parse(ctx)
    assert isinstance(result, dict)
    assert "name" in result
    assert result["name"] == "hello"
    assert result["count"] == "hello"


def test_multi_column_parse_empty_text() -> None:
    col = MultiColumn({"name": TextColumn()})
    ctx = _ctx("")
    result = col.parse(ctx)
    assert isinstance(result, dict)


def test_multi_column_parse_skip_sentinel_excluded() -> None:
    from scrapers.base.table.columns.types.skip import SkipColumn

    col = MultiColumn({"skip_key": SkipColumn(), "name": TextColumn()})
    ctx = _ctx("hello")
    result = col.parse(ctx)
    assert "skip_key" not in result
    assert result["name"] == "hello"


def test_multi_column_parse_multiple_subcolumns() -> None:
    col = MultiColumn({"a": TextColumn(), "b": TextColumn(), "c": TextColumn()})
    ctx = _ctx("value")
    result = col.parse(ctx)
    assert result == {"a": "value", "b": "value", "c": "value"}


def test_multi_column_apply_writes_to_record() -> None:
    col = MultiColumn({"name": TextColumn()})
    ctx = _ctx("test_val")
    record: dict = {}
    col.apply(ctx, record)
    assert record["name"] == "test_val"
