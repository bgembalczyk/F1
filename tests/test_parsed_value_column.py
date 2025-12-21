import re
import sys
import types

from scrapers.base.table.columns.context import ColumnContext
from scrapers.base.table.columns.types.parsed_value import ParsedValueColumn

bs4_stub = types.ModuleType("bs4")


class _StubTag:
    def __init__(self, attrs=None, text: str = ""):
        self.attrs = attrs or {}
        self.text = text

    def get(self, key, default=None):  # pragma: no cover - simple stub
        return self.attrs.get(key, default)

    def get_text(self, *_, **__):  # pragma: no cover - simple stub
        return self.text

    def find_all(self, *_, **__):  # pragma: no cover - simple stub
        return []

    def find_all_next(self, *_, **__):  # pragma: no cover - simple stub
        return []

    @property
    def contents(self):  # pragma: no cover - simple stub
        return [self.text]


class _StubBeautifulSoup:
    def __init__(self, html: str, *_):  # pragma: no cover - simple stub
        self.html = html

    def find(self, name: str | None = None, *_, **__):
        if name == "a":
            return self._parse_a(self.html)
        return _StubTag()

    def find_all(self, *_, **__):  # pragma: no cover - simple stub
        return []

    def _parse_a(self, html: str) -> _StubTag:
        href_match = re.search(r'href="([^"]*)"', html)
        class_match = re.search(r'class="([^"]*)"', html)
        text_match = re.search(r">([^<]*)<", html)

        attrs = {}
        if href_match:
            attrs["href"] = href_match.group(1)
        if class_match:
            attrs["class"] = class_match.group(1).split()

        return _StubTag(attrs, text_match.group(1) if text_match else "")


bs4_stub.Tag = _StubTag
bs4_stub.BeautifulSoup = _StubBeautifulSoup
sys.modules.setdefault("bs4", bs4_stub)


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
