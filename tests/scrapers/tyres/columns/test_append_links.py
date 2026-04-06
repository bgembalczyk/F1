from __future__ import annotations

from scrapers.base.table.columns.context import ColumnContext
from scrapers.tyres.columns.append_links import AppendLinksColumn


def _ctx(
    *,
    key: str = "manufacturers",
    model_fields: set[str] | None = None,
) -> ColumnContext:
    return ColumnContext(
        header="Manufacturer 1",
        key=key,
        raw_text="Pirelli",
        clean_text="Pirelli",
        links=[{"text": "Pirelli", "url": "/wiki/Pirelli"}],
        cell=None,
        base_url="https://example.com",
        model_fields=model_fields,
    )


def test_apply_appends_links_to_existing_record_list() -> None:
    column = AppendLinksColumn()
    record = {"manufacturers": [{"text": "Dunlop", "url": "u"}]}

    column.apply(_ctx(), record)

    assert len(record["manufacturers"]) == 2
    assert record["manufacturers"][1]["text"] == "Pirelli"


def test_apply_skips_when_value_is_skip_sentinel(monkeypatch) -> None:
    column = AppendLinksColumn()
    record: dict[str, list[dict[str, str | None]]] = {}
    ctx = _ctx()
    monkeypatch.setattr(column, "parse", lambda _ctx: _ctx.skip_sentinel)

    column.apply(ctx, record)

    assert record == {}


def test_apply_skips_when_key_not_in_model_fields() -> None:
    column = AppendLinksColumn()
    record: dict[str, list[dict[str, str | None]]] = {}

    column.apply(_ctx(model_fields={"wins"}), record)

    assert record == {}
