from scrapers.base.table.columns.context import ColumnContext
from scrapers.engines.columns.nested_text import NestedTextColumn


def _ctx(*, key: str = "fuel", clean_text: str = "Petrol", model_fields=None):
    return ColumnContext(
        header="Fuel",
        key=key,
        raw_text=clean_text,
        clean_text=clean_text,
        links=[],
        cell=None,
        base_url="https://en.wikipedia.org",
        model_fields=model_fields,
    )


def test_nested_text_column_parse_and_apply() -> None:
    column = NestedTextColumn("petrol")
    record: dict[str, object] = {}

    column.apply(_ctx(clean_text="Permitted"), record)

    assert record == {"fuel": {"petrol": "Permitted"}}


def test_nested_text_column_applies_none_and_respects_model_fields() -> None:
    column = NestedTextColumn("alcohol")
    record: dict[str, object] = {}
    column.apply(_ctx(clean_text=""), record)
    assert record == {"fuel": {"alcohol": None}}

    blocked: dict[str, object] = {}
    column.apply(_ctx(model_fields={"other"}), blocked)
    assert blocked == {}
