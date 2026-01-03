from scrapers.base.table.columns.context import ColumnContext
from scrapers.grands_prix.columns.constructor_split import ConstructorSplitColumn
from scrapers.grands_prix.columns.race_title_status import RaceTitleStatusColumn
from scrapers.grands_prix.columns.restart_status import RestartStatusColumn


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


def test_race_title_status_column_apply() -> None:
    column = RaceTitleStatusColumn()
    record: dict[str, object] = {}
    column.apply(_ctx("Australian Grand Prix*"), record)

    assert record["race_title"] == {"text": "Australian Grand Prix", "url": None}
    assert record["race_status"] == "active"


def test_restart_status_column_parse() -> None:
    column = RestartStatusColumn()
    parsed = column.parse(_ctx("n"))

    assert parsed == {
        "code": "N",
        "description": "race_was_not_restarted",
    }


def test_constructor_split_column_apply() -> None:
    column = ConstructorSplitColumn()
    record: dict[str, object] = {}
    column.apply(_ctx("McLaren - Honda"), record)

    assert record["chassis_constructor"] == {"text": "McLaren", "url": None}
    assert record["engine_constructor"] == {"text": "Honda", "url": None}
