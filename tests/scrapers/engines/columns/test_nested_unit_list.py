from scrapers.base.table.columns.context import ColumnContext
from scrapers.engines.columns.nested_unit_list import NestedUnitListColumn


def ctx(text: str, *, model_fields=None) -> ColumnContext:
    return ColumnContext(
        header="Header",
        key="maximum_displacement",
        raw_text=text,
        clean_text=text,
        links=[],
        cell=None,
        base_url="https://en.wikipedia.org",
        model_fields=model_fields,
    )


def test_nested_unit_list_parses_regular_and_prohibited_values() -> None:
    column = NestedUnitListColumn("naturally_aspirated")
    assert column.parse(ctx("3.5 L")) == [{"value": 3.5, "unit": "L"}]
    assert column.parse(ctx("Prohibited")) == "prohibited"


def test_nested_unit_list_parses_min_max_variants_and_apply_fallback() -> None:
    column = NestedUnitListColumn("forced_induction")
    parsed = column.parse(ctx("1.5 L min, 2.0 L"))
    assert parsed["min"] == {"value": 1.5, "unit": "L"}
    assert parsed["max"] == {"value": 2.0, "unit": "L"}

    record: dict[str, object] = {}
    column.apply(ctx("", model_fields=None), record)
    assert record["maximum_displacement"]["forced_induction"] == []

    blocked: dict[str, object] = {}
    column.apply(ctx("3.0 L", model_fields={"other"}), blocked)
    assert blocked == {}
