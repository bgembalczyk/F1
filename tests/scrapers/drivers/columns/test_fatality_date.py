# ruff: noqa: E501, PLR2004
from bs4 import BeautifulSoup

from scrapers.base.table.columns.context import ColumnContext
from scrapers.drivers.drivers_columns.fatality_date import FatalityDateColumn


def ctx(
    raw: str,
    clean: str | None = None,
    *,
    model_fields: set[str] | None = None,
) -> ColumnContext:
    cell = BeautifulSoup(f"<td>{raw}</td>", "html.parser").find("td")
    return ColumnContext(
        header="Date of accident",
        key="date",
        raw_text=raw,
        clean_text=clean if clean is not None else raw,
        links=[],
        cell=cell,
        base_url="https://en.wikipedia.org",
        model_fields=model_fields,
    )


def test_apply_writes_both_keys_when_model_fields_is_none() -> None:
    col = FatalityDateColumn()
    record: dict = {}
    col.apply(ctx("2 May 1994"), record)
    assert "date" in record
    assert "formula_category" in record


def test_apply_filters_keys_not_in_model_fields() -> None:
    col = FatalityDateColumn()
    record: dict = {}
    col.apply(ctx("2 May 1994", model_fields={"date"}), record)
    assert "date" in record
    assert "formula_category" not in record


def test_apply_allows_all_keys_when_all_are_in_model_fields() -> None:
    col = FatalityDateColumn()
    record: dict = {}
    col.apply(ctx("2 May 1994", model_fields={"date", "formula_category"}), record)
    assert "date" in record
    assert "formula_category" in record


def test_apply_detects_f2_marker() -> None:
    col = FatalityDateColumn()
    record: dict = {}
    col.apply(ctx("2 May 1994#"), record)
    assert record["formula_category"] == "F2"


def test_apply_defaults_to_f1_when_no_marker() -> None:
    col = FatalityDateColumn()
    record: dict = {}
    col.apply(ctx("2 May 1994"), record)
    assert record["formula_category"] == "F1"
