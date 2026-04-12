# ruff: noqa: E501, PLR2004
import pytest

from scrapers.parsers.infobox.text_utils.circuit.text_processing import (
    CircuitTextProcessing,
)


@pytest.fixture()
def proc() -> CircuitTextProcessing:
    return CircuitTextProcessing()


# ---------------------------------------------------------------------------
# _entity_text  (lines 15-21)
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("val", "expected"),
    [
        ({"text": "Hello"}, "Hello"),
        ({"text": "  trimmed  "}, "trimmed"),
        ({"text": ""}, None),
        ({"text": None}, None),
        (None, None),
        ("plain string", "plain string"),
        ("  ", None),
        (42, "42"),
    ],
)
def test_entity_text(val, expected) -> None:
    assert CircuitTextProcessing._entity_text(val) == expected


# ---------------------------------------------------------------------------
# _entity_url  (lines 25-27)
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("val", "expected"),
    [
        ({"url": "https://example.com"}, "https://example.com"),
        ({"url": None}, None),
        ({"url": ""}, None),
        ({}, None),
        ("not a dict", None),
        (None, None),
    ],
)
def test_entity_url(val, expected) -> None:
    assert CircuitTextProcessing._entity_url(val) == expected


# ---------------------------------------------------------------------------
# _norm_time  (lines 35-40)
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("t", "expected"),
    [
        (None, None),
        (1.5, "1.5"),
        (90, "90"),
        (90.0, "90"),
        ("1:23.456", "1:23.456"),
        ("  spaced  ", "spaced"),
        ("", None),
    ],
)
def test_norm_time(t, expected) -> None:
    assert CircuitTextProcessing._norm_time(t) == expected


# ---------------------------------------------------------------------------
# _get_class_field  (line 49)
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("rec", "expected"),
    [
        ({"series": "F1"}, "F1"),
        ({"category": "GT"}, "GT"),
        ({"class": "LMP1"}, "LMP1"),
        ({"series": "F1", "category": "GT"}, "F1"),
        ({}, None),
        ({"series": None, "category": "GT"}, "GT"),
    ],
)
def test_get_class_field(rec, expected) -> None:
    assert CircuitTextProcessing._get_class_field(rec) == expected


# ---------------------------------------------------------------------------
# _strip_lang_marker_tail_only  (lines 72-74)
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("s", "expected"),
    [
        ("Juan Martín Trucco ( es", "Juan Martín Trucco"),
        ("David Vršecký ( cs", "David Vršecký"),
        ("Normal text", "Normal text"),
        ("", ""),
        ("Name (de)", "Name"),
        ("Name (es)", "Name"),
    ],
)
def test_strip_lang_marker_tail_only(s, expected, proc) -> None:
    assert proc._strip_lang_marker_tail_only(s) == expected


# ---------------------------------------------------------------------------
# _extract_outer_parens  (lines 82-102)
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("hello (world)", "world"),
        ("no parens", None),
        ("", None),
        ("(outer (inner) more)", "outer (inner) more"),
        ("text (a) other (b)", "a"),
        ("unclosed (abc", None),
    ],
)
def test_extract_outer_parens(text, expected) -> None:
    assert CircuitTextProcessing._extract_outer_parens(text) == expected


# ---------------------------------------------------------------------------
# _is_en_wiki  (line 107)
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("url", "expected"),
    [
        ("https://en.wikipedia.org/wiki/Circuit", True),
        ("http://en.wikipedia.org/wiki/Circuit", True),
        ("https://fr.wikipedia.org/wiki/Circuit", False),
        ("", False),
        (None, False),
    ],
)
def test_is_en_wiki(url, expected) -> None:
    assert CircuitTextProcessing._is_en_wiki(url) == expected


# ---------------------------------------------------------------------------
# _choose_richer_entity  (line 111)
# ---------------------------------------------------------------------------


def test_choose_richer_entity_prefers_dict_with_url(proc) -> None:
    a = "plain"
    b = {"text": "plain", "url": "https://en.wikipedia.org/wiki/Plain"}
    result = proc._choose_richer_entity(a, b)
    assert result == b


def test_choose_richer_entity_returns_non_none(proc) -> None:
    assert proc._choose_richer_entity(None, "hello") == "hello"
    assert proc._choose_richer_entity("hello", None) == "hello"
