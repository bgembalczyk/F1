from scrapers.base.table.columns.context import ColumnContext
from scrapers.circuits.columns.circuit_name_status import CircuitNameStatusColumn
from scrapers.circuits.columns.last_length_used import LastLengthUsedColumn

EXPECTED_LAST_LENGTH_USED_KM = 3.78
EXPECTED_LAST_LENGTH_USED_MI = 2.349


def _ctx(raw_text: str, *, clean_text: str | None = None) -> ColumnContext:
    return ColumnContext(
        header="Header",
        key="key",
        raw_text=raw_text,
        clean_text=clean_text or raw_text,
        links=[],
        cell=None,
        base_url="https://en.wikipedia.org",
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

    assert record["last_length_used_km"] == EXPECTED_LAST_LENGTH_USED_KM
    assert record["last_length_used_mi"] == EXPECTED_LAST_LENGTH_USED_MI
