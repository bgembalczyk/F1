from __future__ import annotations

import pytest

from scrapers.base.table.columns.context import ColumnContext
from scrapers.base.table.columns.types.column_factory import IntColumn
from scrapers.base.table.columns.types.range import RangeColumn
from scrapers.base.table.columns.types.text import TextColumn
from scrapers.base.table.columns.types.time_range import TimeRangeColumn
from scrapers.base.table.columns.types.tyre import TyreColumn
from scrapers.base.table.columns.types.unit import UnitColumn
from scrapers.base.table.dsl.column import ColumnRef
from scrapers.base.table.dsl.column import ColumnSpec
from scrapers.base.table.dsl.table_schema import TableSchemaDSL
from scrapers.base.table.dsl.serialization import column_ref_payload
from scrapers.base.table.dsl.serialization import serialize_value
from scrapers.base.table.schema import TableSchemaBuilder


def _ctx(text: str | None, *, links: list[dict] | None = None) -> ColumnContext:
    clean_text = "" if text is None else text
    return ColumnContext(
        header="Header",
        key="key",
        raw_text=text,
        clean_text=clean_text,
        links=links or [],
        cell=None,
        base_url="https://en.wikipedia.org",
    )


# ---- range.py ----

def test_range_column_parse_success_with_shared_suffix() -> None:
    column = RangeColumn(
        lower_column=UnitColumn(unit="kg"),
        upper_column=UnitColumn(unit="kg"),
        shared_suffix="kg",
    )

    parsed = column.parse(_ctx("100-110"))

    assert parsed == {
        "min": {"value": 100.0, "unit": "kg"},
        "max": {"value": 110.0, "unit": "kg"},
    }


def test_range_column_parse_fail_when_underlying_parser_fails() -> None:
    column = RangeColumn(lower_column=UnitColumn(unit="kg"), upper_column=UnitColumn(unit="kg"))

    parsed = column.parse(_ctx("abc-def"))

    assert parsed == {"min": None, "max": None}


def test_range_column_edge_case_single_value_applies_to_both_bounds() -> None:
    column = RangeColumn(lower_column=IntColumn(), upper_column=IntColumn())

    parsed = column.parse(_ctx("42"))

    assert parsed == {"min": 42, "max": 42}


# ---- time_range.py ----

def test_time_range_column_parse_success() -> None:
    parsed = TimeRangeColumn().parse(_ctx("9:00am - 1:30pm"))

    assert parsed == {"start": "09:00", "end": "13:30"}


def test_time_range_column_parse_fail_invalid_time_token() -> None:
    parsed = TimeRangeColumn().parse(_ctx("9am-1:00pm"))

    assert parsed is None


def test_time_range_column_edge_case_empty_input() -> None:
    parsed = TimeRangeColumn().parse(_ctx(""))

    assert parsed is None


# ---- tyre.py ----

def test_tyre_column_parse_success_from_text_tokens() -> None:
    parsed = TyreColumn().parse(_ctx("M/P"))

    assert parsed == [
        {"text": "Michelin", "url": None},
        {"text": "Pirelli", "url": None},
    ]


def test_tyre_column_parse_fail_no_tokens() -> None:
    parsed = TyreColumn().parse(_ctx("   / ,  "))

    assert parsed is None


def test_tyre_column_edge_case_links_take_precedence_and_strip_marks() -> None:
    parsed = TyreColumn().parse(
        _ctx(
            "S",
            links=[
                {
                    "text": "M*",
                    "url": "/wiki/Medium",
                }
            ],
        )
    )

    assert parsed == [{"text": "Michelin", "url": "/wiki/Medium"}]


# ---- unit.py ----

def test_unit_column_parse_success_with_explicit_unit() -> None:
    parsed = UnitColumn(unit="kg").parse(_ctx("1,234 kg"))

    assert parsed == {"value": 1234.0, "unit": "kg"}


def test_unit_column_parse_fail_missing_expected_unit() -> None:
    parsed = UnitColumn(unit="kg").parse(_ctx("1234 lb"))

    assert parsed is None


def test_unit_column_edge_case_partial_range_uses_first_value() -> None:
    parsed = UnitColumn(unit="kg").parse(_ctx("100- kg"))

    assert parsed == {"value": 100.0, "unit": "kg"}


# ---- dsl/serialization.py ----

def test_serialize_value_handles_primitives_types_and_callables() -> None:
    def normalize_unit(unit: str) -> str:
        return unit.lower()

    payload = {
        "num": 1,
        "flag": True,
        "nested": ["x", int],
        "callable": normalize_unit,
    }

    serialized = serialize_value(payload)

    assert serialized["num"] == 1
    assert serialized["flag"] is True
    assert serialized["nested"][0] == "x"
    assert serialized["nested"][1] == "builtins.int"
    assert serialized["callable"].endswith("normalize_unit")


def test_column_ref_payload_supports_column_instance_and_column_ref() -> None:
    instance_spec = ColumnSpec(header="Weight", key="weight", column=UnitColumn(unit="kg"))
    ref_spec = ColumnSpec(
        header="Name",
        key="name",
        column=ColumnRef(
            class_path="scrapers.base.table.columns.types.text.TextColumn",
            kwargs={"strip_chars": "*"},
        ),
    )

    instance_payload = column_ref_payload(instance_spec)
    ref_payload = column_ref_payload(ref_spec)

    assert instance_payload["class_path"].endswith("UnitColumn")
    assert instance_payload["kwargs"]["unit"] == "kg"
    assert ref_payload == {
        "class_path": "scrapers.base.table.columns.types.text.TextColumn",
        "kwargs": {"strip_chars": "*"},
    }


# ---- schema.py ----

def test_table_schema_builder_build_success() -> None:
    schema = (
        TableSchemaBuilder()
        .map("Team", "team", TextColumn())
        .map("Weight", "weight", UnitColumn(unit="kg"))
        .build()
    )

    assert schema.column_map == {"Team": "team", "Weight": "weight"}
    assert isinstance(schema.columns["team"], TextColumn)
    assert isinstance(schema.columns["weight"], UnitColumn)


@pytest.mark.parametrize(
    ("header", "key", "column", "error_type"),
    [
        ("", "k", TextColumn(), TypeError),
        ("H", "", TextColumn(), ValueError),
        ("H", "k", object(), TypeError),
    ],
)
def test_table_schema_builder_map_validation_failures(
    header: str,
    key: str,
    column: object,
    error_type: type[Exception],
) -> None:
    builder = TableSchemaBuilder()

    with pytest.raises(error_type):
        builder.map(header, key, column)  # type: ignore[arg-type]


# ---- DSL round-trip ----

def test_table_schema_dsl_round_trip_semantic_equivalence() -> None:
    original = TableSchemaDSL(
        columns=[
            ColumnSpec(
                header="Window",
                key="window",
                column=ColumnRef(
                    class_path=(
                        "scrapers.base.table.columns.types.time_range.TimeRangeColumn"
                    ),
                    kwargs={},
                ),
            ),
            ColumnSpec(
                header="Tyres",
                key="tyres",
                column=ColumnRef(
                    class_path="scrapers.base.table.columns.types.tyre.TyreColumn",
                    kwargs={},
                ),
            ),
        ]
    )

    serialized = original.to_dict()
    restored = TableSchemaDSL.from_dict(serialized)

    original_semantic = [
        (spec.header, spec.key, spec.column.class_path, dict(spec.column.kwargs))
        for spec in original.columns
    ]
    restored_semantic = [
        (spec.header, spec.key, spec.column.class_path, dict(spec.column.kwargs))
        for spec in restored.columns
    ]

    assert restored_semantic == original_semantic
