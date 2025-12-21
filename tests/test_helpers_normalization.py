import sys
import types

from scrapers.base.helpers.records import merge_two_records
from scrapers.base.helpers.text import split_delimited_text
from scrapers.base.helpers.wiki import clean_wiki_text

try:
    import bs4  # noqa: F401
except Exception:
    bs4_module = types.ModuleType("bs4")

    class Tag:  # type: ignore
        pass

    class BeautifulSoup:  # type: ignore
        def __init__(self, *_args, **_kwargs):
            raise RuntimeError("BeautifulSoup not available in tests")

    bs4_module.Tag = Tag
    bs4_module.BeautifulSoup = BeautifulSoup
    sys.modules["bs4"] = bs4_module


def test_clean_wiki_text_removes_references_and_whitespace():
    text = "  Foo\xa0bar [1] [note 3]  "

    assert clean_wiki_text(text) == "Foo bar"


def test_split_delimited_text_respects_min_parts():
    assert split_delimited_text("a", min_parts=2) == []
    assert split_delimited_text("a, b; c / d") == ["a", "b", "c", "d"]


def test_merge_two_records_prefers_richer_data_and_normalizes_time():
    base = {"driver": {"text": "A"}, "time_seconds": 90.0, "year": "1999"}
    extra = {
        "driver": {"text": "A", "url": "https://example.com"},
        "time": "1:30.0",
        "series": {"text": "F1"},
    }

    merged = merge_two_records(base, extra)

    assert merged["driver"]["url"] == "https://example.com"
    assert merged["time"] == 90.0
    assert "time_seconds" not in merged
