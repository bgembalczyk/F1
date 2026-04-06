# ruff: noqa: E501, PLR2004
import pytest

from scrapers.circuits.infobox.services.lap_record import CircuitLapRecordParser


@pytest.fixture()
def parser() -> CircuitLapRecordParser:
    return CircuitLapRecordParser()


# ---------------------------------------------------------------------------
# _wrap_entity_from_links  (lines 31, 36)
# ---------------------------------------------------------------------------

def test_wrap_entity_none_text(parser) -> None:
    assert parser._wrap_entity_from_links(None, []) is None


def test_wrap_entity_empty_after_clean(parser) -> None:
    # text that becomes empty after stripping lang markers
    assert parser._wrap_entity_from_links("  ", []) is None


def test_wrap_entity_plain_no_links(parser) -> None:
    result = parser._wrap_entity_from_links("Lewis Hamilton", [])
    assert result is not None
    assert result["text"] == "Lewis Hamilton"
    assert result["url"] is None


def test_wrap_entity_with_matching_en_wiki_link(parser) -> None:
    links = [{"text": "Lewis Hamilton", "url": "https://en.wikipedia.org/wiki/Lewis_Hamilton"}]
    result = parser._wrap_entity_from_links("Lewis Hamilton", links)
    assert result is not None
    assert result["url"] == "https://en.wikipedia.org/wiki/Lewis_Hamilton"


def test_wrap_entity_non_en_wiki_link_ignored(parser) -> None:
    links = [{"text": "Lewis Hamilton", "url": "https://fr.wikipedia.org/wiki/Lewis_Hamilton"}]
    result = parser._wrap_entity_from_links("Lewis Hamilton", links)
    assert result is not None
    assert result["url"] is None


def test_wrap_entity_slash_split_link_match(parser) -> None:
    # lines 43-46: split on "/" to find partial link match
    links = [{"text": "Ferrari", "url": "https://en.wikipedia.org/wiki/Ferrari"}]
    result = parser._wrap_entity_from_links("Ferrari/Maserati", links)
    assert result is not None
    assert result["url"] == "https://en.wikipedia.org/wiki/Ferrari"


# ---------------------------------------------------------------------------
# parse_lap_record  (line 67 – no details returns None)
# ---------------------------------------------------------------------------

def test_parse_lap_record_none(parser) -> None:
    assert parser.parse_lap_record(None) is None


def test_parse_lap_record_empty_text(parser) -> None:
    assert parser.parse_lap_record({"text": ""}) is None


def test_parse_lap_record_no_parens_returns_none(parser) -> None:
    # no parentheses → select_details_paren returns [] → returns None
    result = parser.parse_lap_record({"text": "1:23.456", "links": []})
    assert result is None


def test_parse_lap_record_valid(parser) -> None:
    # Time + details in parens: "1:23.456 (Lewis Hamilton, Ferrari, 2019)"
    text = "1:23.456 (Lewis Hamilton, Ferrari, 2019)"
    links = [{"text": "Lewis Hamilton", "url": "https://en.wikipedia.org/wiki/Lewis_Hamilton"}]
    result = parser.parse_lap_record({"text": text, "links": links})
    assert result is not None
    assert "driver" in result


# ---------------------------------------------------------------------------
# build_lap_record  (line 74 – no time)
# ---------------------------------------------------------------------------

def test_build_lap_record_no_time(parser) -> None:
    result = parser.build_lap_record(["Hamilton", "Ferrari", "2019"], [], None)
    assert result is not None
    assert "time" not in result
    assert result.get("year") == "2019"


def test_build_lap_record_minimal(parser) -> None:
    result = parser.build_lap_record(["Hamilton"], [], 83.456)
    assert result is not None
    assert result.get("time") == 83.456


def test_build_lap_record_with_series(parser) -> None:
    links = [{"text": "Formula One", "url": "https://en.wikipedia.org/wiki/Formula_One"}]
    result = parser.build_lap_record(["Hamilton", "Ferrari", "2019", "Formula One"], links, 83.456)
    assert result.get("series") is not None


def test_build_lap_record_empty_details(parser) -> None:
    # no driver/vehicle/year/series → empty dict
    result = parser.build_lap_record([], [], None)
    assert result == {}


# ---------------------------------------------------------------------------
# _lap_record_key  (line 109)
# ---------------------------------------------------------------------------

def test_lap_record_key_full(parser) -> None:
    rec = {
        "driver": {"text": "Lewis Hamilton", "url": None},
        "vehicle": {"text": "Mercedes", "url": None},
        "year": "2019",
        "time": 83.456,
    }
    key = parser._lap_record_key(rec)
    assert key is not None
    assert len(key) == 4


def test_lap_record_key_missing_driver(parser) -> None:
    rec = {
        "vehicle": {"text": "Mercedes", "url": None},
        "year": "2019",
        "time": 83.456,
    }
    assert parser._lap_record_key(rec) is None


# ---------------------------------------------------------------------------
# same_lap_record  (line 138)
# ---------------------------------------------------------------------------

def test_same_lap_record_equal(parser) -> None:
    rec = {
        "driver": {"text": "Lewis Hamilton", "url": None},
        "vehicle": {"text": "Mercedes", "url": None},
        "year": "2019",
        "time": 83.456,
    }
    assert parser.same_lap_record(rec, rec) is True


def test_same_lap_record_different(parser) -> None:
    r1 = {
        "driver": {"text": "Lewis Hamilton", "url": None},
        "vehicle": {"text": "Mercedes", "url": None},
        "year": "2019",
        "time": 83.456,
    }
    r2 = {
        "driver": {"text": "Max Verstappen", "url": None},
        "vehicle": {"text": "Red Bull", "url": None},
        "year": "2021",
        "time": 82.0,
    }
    assert parser.same_lap_record(r1, r2) is False


def test_same_lap_record_empty(parser) -> None:
    assert parser.same_lap_record({}, {}) is False


# ---------------------------------------------------------------------------
# _upsert_lap_record  (lines 148-167)
# ---------------------------------------------------------------------------

def test_upsert_lap_record_none_candidate(parser) -> None:
    records: list = []
    parser._upsert_lap_record(None, records)
    assert records == []


def test_upsert_lap_record_no_key_appends(parser) -> None:
    # record without enough fields → key is None → appended directly
    records: list = []
    candidate = {"driver": {"text": "Hamilton", "url": None}}
    parser._upsert_lap_record(candidate, records)
    assert len(records) == 1
    assert records[0]["race_lap_record"] == candidate


def test_upsert_lap_record_new_appends(parser) -> None:
    records: list = []
    candidate = {
        "driver": {"text": "Lewis Hamilton", "url": None},
        "vehicle": {"text": "Mercedes", "url": None},
        "year": "2019",
        "time": 83.456,
    }
    parser._upsert_lap_record(candidate, records)
    assert len(records) == 1


def test_upsert_lap_record_duplicate_merges(parser) -> None:
    existing = {
        "driver": {"text": "Lewis Hamilton", "url": None},
        "vehicle": {"text": "Mercedes", "url": None},
        "year": "2019",
        "time": 83.456,
    }
    records: list = [{"race_lap_record": existing}]
    candidate = {
        "driver": {"text": "Lewis Hamilton", "url": "https://en.wikipedia.org/wiki/Lewis_Hamilton"},
        "vehicle": {"text": "Mercedes", "url": None},
        "year": "2019",
        "time": 83.456,
    }
    parser._upsert_lap_record(candidate, records)
    # still only one record after merging duplicates
    assert len(records) == 1
