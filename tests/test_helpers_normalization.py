import sys
import types

import pytest

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

from scrapers.base.helpers.record_keys import record_key
from scrapers.base.helpers.record_merging import merge_two_records
from scrapers.base.helpers.text_processing import norm_driver_text, safe_text, vehicle_prefix_match
from scrapers.base.helpers.time_processing import simplify_time, time_key, time_seconds
from scrapers.base.helpers.utils import clean_wiki_text, split_delimited_text


def test_clean_wiki_text_removes_references_and_whitespace():
    text = "  Foo\xa0bar [1] [note 3]  "

    assert clean_wiki_text(text) == "Foo bar"


def test_split_delimited_text_respects_min_parts():
    assert split_delimited_text("a", min_parts=2) == []
    assert split_delimited_text("a, b; c / d") == ["a", "b", "c", "d"]


def test_text_normalization_helpers():
    assert safe_text({"text": " John Doe "}) == "john doe"
    assert norm_driver_text("John Doe (test)") == "john doe"
    assert vehicle_prefix_match("Ralt RT4 Cosworth", "Ralt RT4", min_len=4)


def test_time_seconds_parses_multiple_inputs():
    assert time_seconds({"time_seconds": 61.2}) == 61.2
    assert time_seconds({"time": "1:01.2"}) == 61.2
    assert time_seconds({"time": "bad"}) is None


def test_time_key_parses_or_normalizes_text():
    assert time_key({"time": {"seconds": 62}}) == 62.0
    assert time_key({"time": "1:02.5"}) == 62.5
    assert time_key({"time": "DNF"}) == "dnf"


def test_simplify_time_updates_record_in_place():
    record = {"time": {"seconds": 90.0}}
    simplify_time(record)
    assert record["time"] == 90.0

    record = {"time": {"text": "1:02.5"}}
    simplify_time(record)
    assert record["time"] == 62.5

    record = {"time": {"text": "n/a"}}
    simplify_time(record)
    assert record["time"] == "n/a"


def test_record_key_normalizes_time_and_year():
    record = {
        "driver": {"text": "A"},
        "vehicle": "Car",
        "date": {"iso": "1999-01-01"},
        "time": "1:30.0",
    }

    assert record_key(record) == ("a", "car", "1999", 90.0)


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
