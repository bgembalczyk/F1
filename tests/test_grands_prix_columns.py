from scrapers.base.table.columns.context import ColumnContext
from scrapers.base.table.columns.types.restart_status import RestartStatusColumn
from scrapers.columns.types.multi.constructor_split import ConstructorSplitColumn
from scrapers.columns.types.multi.name_status_column.race_title_status import (
    RaceTitleStatusColumn,
)


def ctx(raw_text: str, *, clean_text: str | None = None) -> ColumnContext:
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


def test_race_title_status_column_apply() -> None:
    column = RaceTitleStatusColumn()
    record: dict[str, object] = {}
    column.apply(ctx("Australian Grand Prix*"), record)

    assert record["race_title"] == {"text": "Australian Grand Prix", "url": None}
    assert record["race_status"] == "active"


def test_restart_status_column_parse() -> None:
    column = RestartStatusColumn()
    parsed = column.parse(ctx("n"))

    assert parsed == {
        "code": "N",
        "description": "race_was_not_restarted",
    }


def test_constructor_split_column_apply() -> None:
    column = ConstructorSplitColumn()
    record: dict[str, object] = {}
    column.apply(ctx("McLaren - Honda"), record)

    assert record["chassis_constructor"] == {"text": "McLaren", "url": None}
    assert record["engine_constructor"] == {"text": "Honda", "url": None}
