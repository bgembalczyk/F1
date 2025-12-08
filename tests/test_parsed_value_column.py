from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))

try:
    from bs4 import Tag  # type: ignore
except Exception:
    from tests.bs4_stub import Tag  # type: ignore

from scrapers.base.table.columns.context import ColumnContext
from scrapers.base.table.columns.types.parsed_value import ParsedValueColumn


def _ctx(clean_text: str) -> ColumnContext:
    return ColumnContext(
        header="header",
        key="value",
        raw_text="ignored",
        clean_text=clean_text,
        links=[],
        cell=None,
        skip_sentinel=object(),
    )


def test_parsed_value_column_parses_numbers_from_default_map():
    int_column = ParsedValueColumn(int)
    float_column = ParsedValueColumn(float)

    assert int_column.parse(_ctx("1,234")) == 1234
    assert float_column.parse(_ctx("405.5 pts")) == 405.5


def test_parsed_value_column_respects_custom_parser_for_type():
    column = ParsedValueColumn(list, parser=lambda text: text.split(","))

    assert column.parse(_ctx("a,b,c")) == ["a", "b", "c"]
