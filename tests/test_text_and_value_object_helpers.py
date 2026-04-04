import pytest
from bs4 import BeautifulSoup

from models.value_objects.normalized_date import NormalizedDate
from scrapers.base.helpers.text import choose_richer_entity
from scrapers.base.helpers.text import clean_wiki_text
from scrapers.base.helpers.text import coerce_text
from scrapers.base.helpers.text import extract_text_and_url
from scrapers.base.helpers.text import normalize_dashes
from scrapers.base.helpers.text import strip_lang_suffix
from scrapers.base.helpers.text import strip_marks
from scrapers.base.helpers.text_normalization import clean_infobox_text
from scrapers.base.helpers.text_normalization import drop_empty_fields
from scrapers.base.helpers.text_normalization import is_language_link
from scrapers.base.helpers.text_normalization import match_driver_loose
from scrapers.base.helpers.text_normalization import match_vehicle_prefix
from scrapers.base.helpers.text_normalization import normalize_driver_text
from scrapers.base.helpers.text_normalization import normalize_record_keys
from scrapers.base.helpers.text_normalization import normalize_text
from scrapers.base.helpers.text_normalization import split_delimited_text
from scrapers.base.helpers.text_normalization import to_snake_case
from scrapers.base.helpers.value_objects.lap_record import LapRecord
from scrapers.base.helpers.value_objects.normalized_time import NormalizedTime


@pytest.mark.parametrize(
    ("value", "expected_text", "expected_url"),
    [
        ({"text": " Driver A ", "url": " /wiki/a "}, "Driver A", "/wiki/a"),
        (
            {"name": "Driver B", "url": "https://example.com"},
            "Driver B",
            "https://example.com",
        ),
        ({"text": None, "name": None, "url": None}, "", ""),
        ("  Plain value  ", "Plain value", ""),
        (123, "123", ""),
        (None, "", ""),
    ],
)
def test_extract_text_and_url(value, expected_text, expected_url):
    assert extract_text_and_url(value) == (expected_text, expected_url)


@pytest.mark.parametrize(
    ("a", "b", "expected"),
    [
        (None, {"text": "x", "url": "u"}, {"text": "x", "url": "u"}),
        ({"text": "x"}, None, {"text": "x"}),
        ({"text": "x"}, {"text": "x", "url": "u"}, {"text": "x", "url": "u"}),
        ({"text": "ab"}, {"text": "abcd"}, {"text": "abcd"}),
        ({"text": "abcd"}, {"text": "ab"}, {"text": "abcd"}),
    ],
)
def test_choose_richer_entity(a, b, expected):
    assert choose_richer_entity(a, b) == expected


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("A\u2013B", "A-B"),
        ("A\u2014B", "A-B"),
        ("A\u2212B", "A-B"),
        ("A - B", "A-B"),
        ("A - B - C", "A-B-C"),
        ("A - 2024", "A-2024"),
    ],
)
def test_normalize_dashes_unicode_and_spacing(raw, expected):
    assert normalize_dashes(raw) == expected


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("Name (es)", "Name"),
        ("Name ES", "Name"),
        ("Name (fr) de", "Name"),
        ("Name (xx)", "Name (xx)"),
        ("Name", "Name"),
    ],
)
def test_strip_lang_suffix_iterative(raw, expected):
    assert strip_lang_suffix(raw) == expected


@pytest.mark.parametrize(
    ("html", "expected"),
    [
        ("<td>  A\u00a0B  </td>", "A B"),
        ("<td>Driver [1] (es)</td>", "Driver"),
        ("<td>Line&nbsp;Break</td>", "Line Break"),
        ("<td>A \u2013 B</td>", "A-B"),
    ],
)
def test_clean_wiki_text_with_tags_and_refs(html, expected):
    tag = BeautifulSoup(html, "html.parser").td
    assert clean_wiki_text(tag) == expected


def test_clean_wiki_text_can_disable_normalizations():
    raw = " Driver [1] (es) "
    assert (
        clean_wiki_text(
            raw,
            strip_refs=False,
            strip_lang_suffix=False,
            normalize_dashes=False,
        )
        == "Driver [1] (es)"
    )


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        (" *Name†‡✝✚~^ ", "Name"),
        ("NoMarks", "NoMarks"),
    ],
)
def test_strip_marks(raw, expected):
    assert strip_marks(raw) == expected


@pytest.mark.parametrize(
    ("text", "url", "expected"),
    [
        ("fr", "https://fr.wikipedia.org/wiki/F1", True),
        ("es", "http://es.wikipedia.org/wiki/F1", True),
        ("de", "https://wikipedia.org/de/Formula_One", True),
        ("fr", "https://en.wikipedia.org/wiki/F1", False),
        ("xx", "https://xx.wikipedia.org/wiki/F1", False),
        (None, "https://fr.wikipedia.org/wiki/F1", False),
        ("fr", None, False),
    ],
)
def test_is_language_link(text, url, expected):
    assert is_language_link(text, url) is expected


@pytest.mark.parametrize(
    ("obj", "expected"),
    [
        ({"text": "  FOO  "}, "foo"),
        ("  BAR\n", "bar"),
        (None, ""),
        (123, "123"),
    ],
)
def test_normalize_text(obj, expected):
    assert normalize_text(obj) == expected


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        (" Lewis Hamilton (GBR) ", "lewis hamilton"),
        ("Max   Verstappen", "max verstappen"),
        ({"text": "Charles Leclerc (MON)"}, "charles leclerc"),
        (None, ""),
    ],
)
def test_normalize_driver_text(value, expected):
    assert normalize_driver_text(value) == expected


@pytest.mark.parametrize(
    ("a", "b", "min_len", "expected"),
    [
        ("Lewis Hamilton", "Lewis Hamilton (GBR)", 4, True),
        ("Max", "Max Verstappen", 4, False),
        ("Lando Norris", "Norris", 4, True),
        (None, "Norris", 4, False),
    ],
)
def test_match_driver_loose(a, b, min_len, expected):
    assert match_driver_loose(a, b, min_len=min_len) is expected


@pytest.mark.parametrize(
    ("a", "b", "min_len", "expected"),
    [
        ("McLaren Mercedes MP4-23", "McLaren Mercedes", 10, True),
        ("Ferrari F2004", "Ferrari", 10, False),
        ({"text": "Red Bull RB20"}, "Red Bull", 3, True),
        (None, "Red Bull RB20", 3, False),
    ],
)
def test_match_vehicle_prefix(a, b, min_len, expected):
    assert match_vehicle_prefix(a, b, min_len=min_len) is expected


@pytest.mark.parametrize(
    ("text", "separators", "min_parts", "expected"),
    [
        ("A; B, C / D", r";|,|/", 1, ["A", "B", "C", "D"]),
        ("White, Red (1982, 1984)", r";|,|/", 1, ["White", "Red (1982, 1984)"]),
        ("A • B • C", r"\s*[•·]\s*", 1, ["A", "B", "C"]),
        ("A｜B｜C", r"｜", 1, ["A", "B", "C"]),
        ("", r";|,|/", 1, []),
        (None, r";|,|/", 1, []),
        ("only-one", r";|,|/", 2, []),
    ],
)
def test_split_delimited_text_with_unusual_separators(
    text,
    separators,
    min_parts,
    expected,
):
    assert (
        split_delimited_text(text, separators=separators, min_parts=min_parts)
        == expected
    )


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("  Driver Name  ", "Driver Name"),
        ("\u2003", None),
        (None, None),
        (123, None),
    ],
)
def test_clean_infobox_text_none_and_empty(value, expected):
    assert clean_infobox_text(value) == expected


@pytest.mark.parametrize(
    ("record", "expected"),
    [
        (
            {"Driver Name": "Lewis", "Car-Model": "W14", "!!!": "ignored"},
            {"driver_name": "Lewis", "car_model": "W14"},
        ),
        ({"   ": 1, "A__B": 2}, {"a_b": 2}),
    ],
)
def test_normalize_record_keys(record, expected):
    assert normalize_record_keys(record) == expected


@pytest.mark.parametrize(
    ("record", "expected"),
    [
        (
            {"a": "x", "b": "   ", "c": None, "d": [], "e": {}, "f": 0},
            {"a": "x", "f": 0},
        ),
        ({"name": "  Max  "}, {"name": "  Max  "}),
    ],
)
def test_drop_empty_fields(record, expected):
    assert drop_empty_fields(record) == expected


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("Driver Name", "driver_name"),
        ("___Mixed---Case___", "mixed_case"),
        ("!!!", ""),
    ],
)
def test_to_snake_case(raw, expected):
    assert to_snake_case(raw) == expected


@pytest.mark.parametrize(
    ("value", "expected_text", "expected_seconds"),
    [
        (None, None, None),
        (NormalizedTime(" 1:23.456 ", " 83.456 "), "1:23.456", 83.456),
        ({"text": " 1:22.000 ", "seconds": " 82.0 "}, "1:22.000", 82.0),
        (81.5, None, 81.5),
        (" 1:21.999 ", "1:21.999", None),
        ({"text": " ", "seconds": "bad"}, None, None),
    ],
)
def test_normalized_time_from_value(value, expected_text, expected_seconds):
    result = NormalizedTime.from_value(value)
    if value is None:
        assert result is None
        return
    assert result is not None
    assert result.text == expected_text
    assert result.seconds == expected_seconds


@pytest.mark.parametrize(
    ("record_data", "expected_time", "expected_date_iso", "expect_class_alias"),
    [
        (
            {
                "time": {"text": " 1:23.456 ", "seconds": "83.456"},
                "date": {"text": "7 Jun 2019", "iso": ["2019-06-07"]},
                "class": "GT3",
            },
            {"text": "1:23.456", "seconds": 83.456},
            "2019-06-07",
            True,
        ),
        (
            {"time": "bad-format", "date": "n/a", "class_": "LMP2"},
            "bad-format",
            None,
            True,
        ),
    ],
)
def test_lap_record_post_init_and_to_dict(
    record_data,
    expected_time,
    expected_date_iso,
    expect_class_alias,
):
    record = LapRecord(record_data)

    if isinstance(expected_time, dict):
        assert isinstance(record["time"], NormalizedTime)
    else:
        assert record["time"] == expected_time

    if expected_date_iso is not None:
        assert isinstance(record["date"], NormalizedDate)
        assert record["date"].iso == expected_date_iso

    assert ("class_" in record.data) is expect_class_alias
    exported = record.to_dict()
    assert exported["time"] == expected_time


def test_lap_record_mapping_behaviour_and_setitem_normalization():
    record = LapRecord({})
    record.setdefault("laps", 10)
    record.setdefault("laps", 99)

    record["time"] = {"text": " 1:30.000 ", "seconds": "90"}
    record["date"] = {"text": "June 7, 2019", "iso": "2019-06-07"}

    assert record.get("laps") == 10
    assert isinstance(record["time"], NormalizedTime)
    assert record["time"].seconds == 90.0
    assert isinstance(record["date"], NormalizedDate)
    assert record.pop("missing", "fallback") == "fallback"

    keys = list(record.keys())
    assert "laps" in keys and "time" in keys and "date" in keys


def test_coerce_text_supports_bs4_tag():
    tag = BeautifulSoup("<span> Hello <b>World</b> </span>", "html.parser").span
    assert coerce_text(tag) == "Hello World"
    assert coerce_text(None) == ""
