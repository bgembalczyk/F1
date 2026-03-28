# ruff: noqa: E501, PLR2004, RUF001, RUF002, RUF003, SLF001, ARG001, ARG002, N802, B017, PT011, PT017, E402, PT001, PLC0415, RUF100
from models.value_objects.normalized_date import NormalizedDate
from scrapers.base.helpers.value_objects.normalized_time import NormalizedTime
from scrapers.base.table.columns.context import ColumnContext
from scrapers.base.table.columns.types.date import DateColumn
from scrapers.base.table.columns.types.parsed_value import ParsedValueColumn
from scrapers.base.table.columns.types.time import TimeColumn
from tests.support.compat_stubs import ensure_bs4_stub

ensure_bs4_stub()


def _ctx(clean_text: str) -> ColumnContext:
    return ColumnContext(
        header="header",
        key="value",
        raw_text="ignored",
        clean_text=clean_text,
        links=[],
        cell=None,
        base_url="https://en.wikipedia.org",
    )


def test_parsed_value_column_parses_numbers_from_default_map():
    int_column = ParsedValueColumn(int)
    float_column = ParsedValueColumn(float)

    assert int_column.parse(_ctx("1,234")) == 1234
    assert float_column.parse(_ctx("405.5 pts")) == 405.5


def test_parsed_value_column_respects_custom_parser_for_type():
    column = ParsedValueColumn(list, parser=lambda text: text.split(","))

    assert column.parse(_ctx("a,b,c")) == ["a", "b", "c"]


def test_date_and_time_columns_return_normalized_value_objects():
    date_column = DateColumn()
    time_column = TimeColumn()

    date_value = date_column.parse(_ctx("7 June 2019"))
    time_value = time_column.parse(_ctx("1:23.456"))

    assert isinstance(date_value, NormalizedDate)
    assert date_value.to_dict() == {"text": "7 June 2019", "iso": "2019-06-07"}
    assert isinstance(time_value, NormalizedTime)
    assert time_value.to_dict() == {"text": "1:23.456", "seconds": 83.456}
