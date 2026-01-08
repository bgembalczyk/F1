from scrapers.base.table.columns.context import ColumnContext
from scrapers.drivers.columns.driver_name_status import DriverNameStatusColumn
from scrapers.drivers.columns.entries_starts import EntriesStartsColumn
from scrapers.drivers.columns.fatality_date import FatalityDateColumn
from scrapers.drivers.columns.fatality_event import FatalityEventColumn


def _ctx(
    raw_text: str,
    *,
    clean_text: str | None = None,
    links: list[dict] | None = None,
    model_fields: set[str] | None = None,
) -> ColumnContext:
    return ColumnContext(
        header="Header",
        key="key",
        raw_text=raw_text,
        clean_text=clean_text or raw_text,
        links=links or [],
        cell=None,
        base_url="https://en.wikipedia.org",
        model_fields=model_fields,
    )


def test_driver_name_status_column_apply() -> None:
    column = DriverNameStatusColumn()
    record: dict[str, object] = {}
    column.apply(_ctx("Jane Doe*"), record)

    assert record["driver"] == {"text": "Jane Doe", "url": None}
    assert record["is_active"] is True
    assert record["is_world_champion"] is False


def test_driver_name_status_column_active_champion() -> None:
    column = DriverNameStatusColumn()
    record: dict[str, object] = {}
    column.apply(_ctx("John Doe~"), record)

    assert record["is_active"] is True
    assert record["is_world_champion"] is True


def test_entries_starts_column_apply() -> None:
    column = EntriesStartsColumn()
    record: dict[str, object] = {}
    column.apply(_ctx("12 (10)"), record)

    assert record["entries"] == 12
    assert record["starts"] == 10


def test_fatality_date_column_parse() -> None:
    column = FatalityDateColumn()
    parsed = column.parse(_ctx("11 June 1950#"))

    assert parsed["date"] == "1950-06-11"
    assert parsed["formula_category"] == "F2"


def test_fatality_event_column_parse() -> None:
    column = FatalityEventColumn()
    parsed = column.parse(_ctx("1958 French Grand Prix†"))

    assert parsed["event"] == "1958 French Grand Prix"
    assert parsed["championship"] is False
