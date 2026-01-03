from scrapers.base.table.columns.context import ColumnContext
from scrapers.circuits.columns.circuit_name_status import CircuitNameStatusColumn
from scrapers.circuits.columns.last_length_used import LastLengthUsedColumn


def _ctx(raw_text: str, *, clean_text: str | None = None) -> ColumnContext:
    return ColumnContext(
        header="Header",
        key="key",
        raw_text=raw_text,
        clean_text=clean_text or raw_text,
        links=[],
        cell=None,
        model_fields=None,
    )


def test_circuit_name_status_column_apply() -> None:
    column = CircuitNameStatusColumn()
    record: dict[str, object] = {}
    column.apply(_ctx("Autodromo Nazionale Monza*"), record)

    assert record["circuit"] == {"text": "Autodromo Nazionale Monza", "url": None}
    assert record["circuit_status"] == "current"


def test_last_length_used_column_apply() -> None:
    column = LastLengthUsedColumn()
    record: dict[str, object] = {}
    column.apply(_ctx("3.780 km (2.349 mi)"), record)

    assert record["last_length_used_km"] == 3.78
    assert record["last_length_used_mi"] == 2.349
