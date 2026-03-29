# ruff: noqa: E501, PLR2004, RUF001, RUF002, RUF003, SLF001, ARG001, ARG002, N802, B017, PT011, PT017, E402, PT001, PLC0415, RUF100
"""Tests for sponsorship liveries column fixes."""

from unittest.mock import MagicMock

import pytest

from scrapers.base.table.columns.context import ColumnContext
from scrapers.sponsorship_liveries.columns.seasons import SponsorshipSeasonsColumn
from scrapers.sponsorship_liveries.columns.sponsor import SponsorColumn
from scrapers.sponsorship_liveries.parsers.section import SponsorshipSectionParser
from scrapers.sponsorship_liveries.parsers.splitters.record.facade import (
    SponsorshipRecordSplitter,
)


def _ctx(
    raw_text: str,
    *,
    clean_text: str | None = None,
    links: list[dict] | None = None,
) -> ColumnContext:
    return ColumnContext(
        header="Header",
        key="key",
        raw_text=raw_text,
        clean_text=clean_text or raw_text,
        links=links or [],
        cell=None,
        base_url="https://en.wikipedia.org",
    )


# ── Fix 1 & 2: implicit split after closing paren ─────────────────────────────


def test_split_after_paren_no_separator_year_scope() -> None:
    """Lotus case: 'Elf (1983–1986) Goodyear (1984–1986) Olympus (1985)' splits into 3."""
    col = SponsorColumn()
    result = col._parse_text_with_links(
        "Elf (1983\u20131986) Goodyear (1984\u20131986) Olympus (1985)",
        [],
    )
    assert len(result) == 3
    texts = [r if isinstance(r, str) else r.get("text") for r in result]
    assert texts[0] == "Elf"
    assert texts[1] == "Goodyear"
    assert texts[2] == "Olympus"


def test_split_after_paren_preserves_year_params() -> None:
    """Year params are preserved on each split item."""
    col = SponsorColumn()
    result = col._parse_text_with_links(
        "Elf (1983\u20131986) Goodyear (1984\u20131986)",
        [],
    )
    assert len(result) == 2
    elf = result[0]
    goodyear = result[1]
    assert isinstance(elf, dict)
    assert elf.get("text") == "Elf"
    assert isinstance(goodyear, dict)
    assert goodyear.get("text") == "Goodyear"
    # Year params should still be on each item (em-dash is normalised to hyphen)
    assert elf.get("params") == ["1983-1986"]
    assert goodyear.get("params") == ["1984-1986"]


def test_split_after_paren_no_separator_gp_scope() -> None:
    """March case: GP-scope sponsors not separated by commas split correctly."""
    col = SponsorColumn()
    result = col._parse_text_with_links(
        "Monaco Fine Arts Gallery (Monaco Grand Prix only) "
        "Macconal-Mason Gallery Fine Paintings (British Grand Prix only)",
        [],
    )
    assert len(result) == 2
    texts = [r if isinstance(r, str) else r.get("text") for r in result]
    assert texts[0] == "Monaco Fine Arts Gallery"
    assert texts[1] == "Macconal-Mason Gallery Fine Paintings"


def test_split_after_paren_with_trailing_explicit_separator() -> None:
    """Regular comma/semicolon after paren still works correctly."""
    col = SponsorColumn()
    result = col._parse_text_with_links("Courage (1981); Champion (1983)", [])
    assert len(result) == 2
    assert (
        result[0] if isinstance(result[0], str) else result[0].get("text")
    ) == "Courage"
    assert (
        result[1] if isinstance(result[1], str) else result[1].get("text")
    ) == "Champion"


def test_no_split_without_paren() -> None:
    """Plain comma-separated list still works as before."""
    col = SponsorColumn()
    result = col._parse_text_with_links("Essex, Tissot, Courage", [])
    assert len(result) == 3


def test_mixed_explicit_and_implicit_separators() -> None:
    """Mix of explicit separators and implicit paren splits."""
    col = SponsorColumn()
    result = col._parse_text_with_links(
        "Renault (1983\u20131986); Elf (1983\u20131986) Goodyear (1984\u20131986)",
        [],
    )
    assert len(result) == 3
    texts = [r if isinstance(r, str) else r.get("text") for r in result]
    assert texts == ["Renault", "Elf", "Goodyear"]


# ── Fix 3: Matra – "car" keyword routes to "car" field, not "driver" ──────────


def test_season_column_car_keyword_sets_car_field() -> None:
    """When Gemini classifies parenthetical as car_model, linked item is stored under 'car'."""
    classification = {
        "driver": [],
        "car_model": ["Matra MS9"],
        "engine_constructor": [],
        "grand_prix": [],
        "time_period": [],
        "other": [],
    }
    col = SponsorshipSeasonsColumn(
        team_name="Matra",
        classifier=_make_classifier(classification),
    )
    record: dict = {}
    col.apply(
        _ctx(
            "1968 (Matra MS9 car)",
            links=[
                {
                    "text": "Matra MS9",
                    "url": "https://en.wikipedia.org/wiki/Matra_MS9",
                },
            ],
        ),
        record,
    )
    assert "car" in record
    assert "driver" not in record
    assert record["car"] == [
        {"text": "Matra MS9", "url": "https://en.wikipedia.org/wiki/Matra_MS9"},
    ]


def test_season_column_no_car_keyword_sets_driver_field() -> None:
    """When Gemini classifies parenthetical as driver, linked item is stored under 'driver'."""
    classification = {
        "driver": ["James Hunt"],
        "car_model": [],
        "engine_constructor": [],
        "grand_prix": [],
        "time_period": [],
        "other": [],
    }
    col = SponsorshipSeasonsColumn(
        team_name="McLaren",
        classifier=_make_classifier(classification),
    )
    record: dict = {}
    col.apply(
        _ctx(
            "1976 (James Hunt)",
            links=[
                {
                    "text": "James Hunt",
                    "url": "https://en.wikipedia.org/wiki/James_Hunt",
                },
            ],
        ),
        record,
    )
    assert "driver" in record
    assert "car" not in record
    assert record["driver"] == [
        {"text": "James Hunt", "url": "https://en.wikipedia.org/wiki/James_Hunt"},
    ]


def test_season_column_no_classifier_skips_paren_fields() -> None:
    """Without a classifier, parenthetical content is ignored (no car/driver/grand_prix_scope)."""
    col = SponsorshipSeasonsColumn()
    record: dict = {}
    col.apply(
        _ctx(
            "1968 (Matra MS9 car)",
            links=[
                {"text": "Matra MS9", "url": "https://en.wikipedia.org/wiki/Matra_MS9"},
            ],
        ),
        record,
    )
    assert "car" not in record
    assert "driver" not in record
    assert "grand_prix_scope" not in record
    assert "paren_classification" not in record


def test_season_column_gemini_sets_grand_prix_scope() -> None:
    """When Gemini classifies parenthetical as grand_prix, grand_prix_scope is set with link URL."""
    classification = {
        "driver": [],
        "car_model": [],
        "engine_constructor": [],
        "grand_prix": ["Chinese Grand Prix"],
        "time_period": [],
        "other": [],
    }
    col = SponsorshipSeasonsColumn(
        team_name="Ferrari",
        classifier=_make_classifier(classification),
    )
    record: dict = {}
    col.apply(
        _ctx(
            "2004 (only Chinese GP)",
            links=[
                {
                    "text": "Chinese Grand Prix",
                    "url": "https://en.wikipedia.org/wiki/Chinese_Grand_Prix",
                },
            ],
        ),
        record,
    )
    assert record.get("_season_scoped_gp") is True
    assert record["grand_prix_scope"]["type"] == "only"
    assert record["grand_prix_scope"]["grand_prix"] == [
        {
            "text": "Chinese Grand Prix",
            "url": "https://en.wikipedia.org/wiki/Chinese_Grand_Prix",
        },
    ]
    assert "driver" not in record
    assert "car" not in record


def test_season_column_gemini_grand_prix_fallback_to_text_when_no_links() -> None:
    """When Gemini returns grand_prix names but no matching links exist, text-only entries are used."""
    classification = {
        "driver": [],
        "car_model": [],
        "engine_constructor": [],
        "grand_prix": ["Monaco Grand Prix"],
        "time_period": [],
        "other": [],
    }
    col = SponsorshipSeasonsColumn(
        team_name="Ferrari",
        classifier=_make_classifier(classification),
    )
    record: dict = {}
    col.apply(_ctx("2004 (only Monaco GP)"), record)

    assert record.get("_season_scoped_gp") is True
    assert record["grand_prix_scope"]["grand_prix"] == [{"text": "Monaco Grand Prix"}]


def test_season_column_gemini_empty_classification_sets_no_extra_fields() -> None:
    """When Gemini returns no meaningful classifications, no extra fields are set on the record."""
    classification = {
        "driver": [],
        "car_model": [],
        "engine_constructor": [],
        "grand_prix": [],
        "time_period": [],
        "other": ["never raced"],
    }
    col = SponsorshipSeasonsColumn(
        team_name="Coloni",
        classifier=_make_classifier(classification),
    )
    record: dict = {}
    col.apply(_ctx("1990 (never raced)"), record)

    assert "paren_classification" not in record
    assert "driver" not in record
    assert "car" not in record
    assert "engine" not in record
    assert "grand_prix_scope" not in record


# ── Fix 4: McLaren – comma inside link text not treated as separator ───────────


def test_comma_inside_link_not_split() -> None:
    """Comma that is part of a linked sponsor name (e.g. 'CA, Inc.') is not a separator."""
    col = SponsorColumn()
    links = [
        {
            "text": "CA, Inc.",
            "url": "https://en.wikipedia.org/wiki/CA,_Inc.",
        },
    ]
    result = col._parse_text_with_links("CA, Inc. (1997\u20132002)", links)
    assert len(result) == 1
    item = result[0]
    assert isinstance(item, dict)
    assert item.get("text") == "CA, Inc."
    assert item.get("url") == "https://en.wikipedia.org/wiki/CA,_Inc."


def test_comma_between_separate_sponsors_still_splits() -> None:
    """Commas between distinct sponsors (not inside any link) still split correctly."""
    col = SponsorColumn()
    links = [
        {"text": "Sponsor A", "url": "https://en.wikipedia.org/wiki/A"},
        {"text": "Sponsor B", "url": "https://en.wikipedia.org/wiki/B"},
    ]
    result = col._parse_text_with_links("Sponsor A, Sponsor B", links)
    assert len(result) == 2
    assert result[0].get("text") == "Sponsor A"
    assert result[1].get("text") == "Sponsor B"


# ── Gemini-based paren classifier ────────────────────────────────────────────


def _make_classifier(classification: dict):
    """Create a mock ParenClassifier that always returns *classification*."""
    classifier = MagicMock()
    classifier.classify.return_value = classification
    return classifier


def test_gemini_classifier_called_for_paren() -> None:
    """When a parenthetical is present, the classifier.classify() method is called."""
    classification = {
        "driver": [],
        "car_model": ["Dallara F188"],
        "engine_constructor": [],
        "grand_prix": [],
        "time_period": [],
        "other": [],
    }
    classifier = _make_classifier(classification)
    col = SponsorshipSeasonsColumn(team_name="Scuderia Italia", classifier=classifier)
    record: dict = {}
    col.apply(_ctx("1988 (Dallara F188)"), record)

    classifier.classify.assert_called_once()
    call_kwargs = classifier.classify.call_args.kwargs
    assert call_kwargs["paren_content"] == "Dallara F188"
    assert call_kwargs["team_name"] == "Scuderia Italia"
    assert call_kwargs["year_text"] == "1988"


def test_gemini_classification_stored_in_record() -> None:
    """When Gemini classifies as car_model the 'car' field is set on the record."""
    classification = {
        "driver": [],
        "car_model": ["Dallara F188"],
        "engine_constructor": [],
        "grand_prix": [],
        "time_period": [],
        "other": [],
    }
    col = SponsorshipSeasonsColumn(
        team_name="Scuderia Italia",
        classifier=_make_classifier(classification),
    )
    record: dict = {}
    col.apply(_ctx("1988 (Dallara F188)"), record)

    assert "paren_classification" not in record
    assert record["car"] == [{"text": "Dallara F188"}]


def test_no_gemini_call_without_paren() -> None:
    """When there is no parenthetical, the classifier is never called."""
    classifier = _make_classifier({})
    col = SponsorshipSeasonsColumn(team_name="Team A", classifier=classifier)
    record: dict = {}
    col.apply(_ctx("1988"), record)

    classifier.classify.assert_not_called()
    assert "paren_classification" not in record


def test_no_gemini_call_without_classifier() -> None:
    """When no classifier is configured, no 'paren_classification' key is added."""
    col = SponsorshipSeasonsColumn()
    record: dict = {}
    col.apply(_ctx("1988 (Dallara F188)"), record)

    assert "paren_classification" not in record


def test_gemini_table_headers_forwarded() -> None:
    """Table headers are forwarded to classifier.classify()."""
    headers = ["Year", "Main colour(s)", "Main sponsor(s)"]
    classification = {
        "driver": [],
        "car_model": [],
        "engine_constructor": ["Subaru"],
        "grand_prix": [],
        "time_period": [],
        "other": [],
    }
    classifier = _make_classifier(classification)
    col = SponsorshipSeasonsColumn(
        team_name="Coloni",
        classifier=classifier,
        table_headers=headers,
    )
    record: dict = {}
    col.apply(_ctx("1990 (with Subaru power)"), record)

    call_kwargs = classifier.classify.call_args.kwargs
    assert call_kwargs["headers"] == headers


def test_season_column_engine_constructor_sets_engine_field() -> None:
    """When Gemini classifies as engine_constructor, the 'engine' field is set."""
    classification = {
        "driver": [],
        "car_model": [],
        "engine_constructor": ["Subaru"],
        "grand_prix": [],
        "time_period": [],
        "other": [],
    }
    col = SponsorshipSeasonsColumn(
        team_name="Coloni",
        classifier=_make_classifier(classification),
    )
    record: dict = {}
    col.apply(
        _ctx(
            "1990 (with Subaru power)",
            links=[
                {
                    "text": "1990",
                    "url": "https://en.wikipedia.org/wiki/1990_Formula_One_season",
                },
                {"text": "Subaru", "url": "https://en.wikipedia.org/wiki/Subaru"},
            ],
        ),
        record,
    )
    assert "engine" in record
    assert "car" not in record
    assert "driver" not in record
    assert record["engine"] == [
        {"text": "Subaru", "url": "https://en.wikipedia.org/wiki/Subaru"},
    ]


def test_season_column_engine_constructor_text_only_fallback() -> None:
    """When engine_constructor is classified but no links present, text-only entry is used."""
    classification = {
        "driver": [],
        "car_model": [],
        "engine_constructor": ["Subaru"],
        "grand_prix": [],
        "time_period": [],
        "other": [],
    }
    col = SponsorshipSeasonsColumn(
        team_name="Coloni",
        classifier=_make_classifier(classification),
    )
    record: dict = {}
    col.apply(_ctx("1990 (with Subaru power)"), record)

    assert record["engine"] == [{"text": "Subaru"}]


def test_hallucination_values_not_in_cell_text_are_ignored() -> None:
    """Classified values not present in the original cell text are treated as hallucinations."""
    classification = {
        "driver": [],
        "car_model": ["Coloni C3B"],
        "engine_constructor": ["Ford"],
        "grand_prix": [],
        "time_period": [],
        "other": [],
    }
    col = SponsorshipSeasonsColumn(
        team_name="Coloni",
        classifier=_make_classifier(classification),
    )
    record: dict = {}
    # Neither "Coloni C3B" nor "Ford" appear in the cell text.
    col.apply(_ctx("1990 (without Subaru power)"), record)

    assert "car" not in record
    assert "engine" not in record
    assert "driver" not in record
    assert "grand_prix_scope" not in record


def test_hallucination_only_matching_values_kept() -> None:
    """Only classified values that appear in the cell text survive the hallucination filter."""
    classification = {
        "driver": [],
        "car_model": [],
        "engine_constructor": ["Subaru", "Ford"],
        "grand_prix": [],
        "time_period": [],
        "other": [],
    }
    col = SponsorshipSeasonsColumn(
        team_name="Coloni",
        classifier=_make_classifier(classification),
    )
    record: dict = {}
    # "Subaru" is in the cell text but "Ford" is not.
    col.apply(_ctx("1990 (with Subaru power)"), record)

    assert "engine" in record
    assert record["engine"] == [{"text": "Subaru"}]


def test_gemini_classifier_exception_does_not_propagate() -> None:
    """If classifier.classify() raises, the column still sets the season field."""
    from infrastructure.gemini.client import GeminiClient
    from infrastructure.gemini.errors import GeminiTransportError
    from scrapers.sponsorship_liveries.helpers.paren_classifier import ParenClassifier

    mock_client = MagicMock(spec=GeminiClient)
    mock_client.query.side_effect = GeminiTransportError("network error")
    classifier = ParenClassifier(mock_client)

    col = SponsorshipSeasonsColumn(team_name="Coloni", classifier=classifier)
    record: dict = {}
    col.apply(_ctx("1990 (with Subaru power)"), record)

    # Season should still be parsed correctly.
    assert "key" in record
    # No extra fields from the failed classification.
    assert "paren_classification" not in record
    assert "driver" not in record
    assert "car" not in record
    assert "engine" not in record
    assert "grand_prix_scope" not in record


def test_gemini_classifier_fail_fast_policy_propagates_error() -> None:
    from infrastructure.gemini.client import GeminiClient
    from infrastructure.gemini.errors import GeminiResponseParseError
    from scrapers.sponsorship_liveries.helpers.paren_classifier import ParenClassifier

    mock_client = MagicMock(spec=GeminiClient)
    mock_client.query.side_effect = GeminiResponseParseError("bad response")
    classifier = ParenClassifier(mock_client).with_error_policy(policy="fail-fast")

    with pytest.raises(GeminiResponseParseError, match="bad response"):
        classifier.classify(
            paren_content="with Subaru power",
            team_name="Coloni",
            year_text="1990",
            headers=["Year"],
        )


# ── Fix 5: McLaren – "Livery principal sponsor(s)" maps to livery_principal_sponsors ──


def test_livery_principal_sponsor_column_maps_to_livery_principal_sponsors() -> None:
    """Column 'Livery principal sponsor(s)' is mapped to the livery_principal_sponsors key."""
    splitter = SponsorshipRecordSplitter()
    parser = SponsorshipSectionParser(
        url="https://en.wikipedia.org",
        include_urls=False,
        normalize_empty_values=True,
        splitter=splitter,
    )
    pipeline = parser._build_pipeline()
    assert "Livery principal sponsor(s)" in pipeline.column_map
    assert (
        pipeline.column_map["Livery principal sponsor(s)"]
        == "livery_principal_sponsors"
    )
