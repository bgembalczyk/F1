"""Tests for sponsorship liveries column fixes."""
from unittest.mock import MagicMock

from bs4 import BeautifulSoup

from scrapers.base.table.columns.context import ColumnContext
from scrapers.sponsorship_liveries.columns.seasons import SponsorshipSeasonsColumn
from scrapers.sponsorship_liveries.columns.sponsor import SponsorColumn
from scrapers.sponsorship_liveries.parsers.colour_scope import ColourScopeHandler


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


def _ctx_with_cell(html: str, *, base_url: str = "https://en.wikipedia.org") -> ColumnContext:
    from scrapers.base.helpers.links import normalize_links
    cell = BeautifulSoup(f"<td>{html}</td>", "html.parser").find("td")
    raw_text = cell.get_text(" ", strip=True)
    links = normalize_links(cell, full_url=lambda href: base_url + href, drop_empty_text=True)
    return ColumnContext(
        header="Sponsor",
        key="sponsor",
        raw_text=raw_text,
        clean_text=raw_text,
        links=links,
        cell=cell,
        base_url=base_url,
    )


# ── Fix 1 & 2: implicit split after closing paren ─────────────────────────────


def test_split_after_paren_no_separator_year_scope() -> None:
    """Lotus case: 'Elf (1983–1986) Goodyear (1984–1986) Olympus (1985)' splits into 3."""
    col = SponsorColumn()
    result = col._parse_text_with_links(
        "Elf (1983\u20131986) Goodyear (1984\u20131986) Olympus (1985)", [],
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
        "Elf (1983\u20131986) Goodyear (1984\u20131986)", [],
    )
    assert len(result) == 2
    elf = result[0]
    goodyear = result[1]
    assert isinstance(elf, dict) and elf.get("text") == "Elf"
    assert isinstance(goodyear, dict) and goodyear.get("text") == "Goodyear"
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
    assert (result[0] if isinstance(result[0], str) else result[0].get("text")) == "Courage"
    assert (result[1] if isinstance(result[1], str) else result[1].get("text")) == "Champion"


def test_no_split_without_paren() -> None:
    """Plain comma-separated list still works as before."""
    col = SponsorColumn()
    result = col._parse_text_with_links("Essex, Tissot, Courage", [])
    assert len(result) == 3


def test_mixed_explicit_and_implicit_separators() -> None:
    """Mix of explicit separators and implicit paren splits."""
    col = SponsorColumn()
    result = col._parse_text_with_links(
        "Renault (1983\u20131986); Elf (1983\u20131986) Goodyear (1984\u20131986)", [],
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
    col = SponsorshipSeasonsColumn(team_name="Matra", classifier=_make_classifier(classification))
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
    col = SponsorshipSeasonsColumn(team_name="McLaren", classifier=_make_classifier(classification))
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
            links=[{"text": "Matra MS9", "url": "https://en.wikipedia.org/wiki/Matra_MS9"}],
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
    col = SponsorshipSeasonsColumn(team_name="Ferrari", classifier=_make_classifier(classification))
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
        {"text": "Chinese Grand Prix", "url": "https://en.wikipedia.org/wiki/Chinese_Grand_Prix"},
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
    col = SponsorshipSeasonsColumn(team_name="Ferrari", classifier=_make_classifier(classification))
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
    col = SponsorshipSeasonsColumn(team_name="Coloni", classifier=_make_classifier(classification))
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
                {"text": "1990", "url": "https://en.wikipedia.org/wiki/1990_Formula_One_season"},
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
    from scrapers.sponsorship_liveries.helpers.paren_classifier import ParenClassifier
    from infrastructure.gemini.client import GeminiClient

    mock_client = MagicMock(spec=GeminiClient)
    mock_client.query.side_effect = RuntimeError("network error")
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

# ── Fix 5: McLaren – "Livery principal sponsor(s)" maps to livery_principal_sponsors ──


def test_livery_principal_sponsor_column_maps_to_livery_principal_sponsors() -> None:
    """Column 'Livery principal sponsor(s)' is mapped to the livery_principal_sponsors key."""
    from scrapers.sponsorship_liveries.parsers.section_parser import SponsorshipSectionParser
    from scrapers.sponsorship_liveries.parsers.record_splitter import SponsorshipRecordSplitter

    splitter = SponsorshipRecordSplitter()
    parser = SponsorshipSectionParser(
        url="https://en.wikipedia.org",
        include_urls=False,
        normalize_empty_values=True,
        splitter=splitter,
    )
    pipeline = parser._build_pipeline()
    assert "Livery principal sponsor(s)" in pipeline.column_map
    assert pipeline.column_map["Livery principal sponsor(s)"] == "livery_principal_sponsors"


# ── Fix 6: Colours – "and" splits colours the same as "or" ───────────────────


def test_split_or_colours_splits_on_and() -> None:
    """'Green and Black' is split into two separate colour entries."""
    result = ColourScopeHandler.split_or_colours(["Green and Black"])
    assert result == ["Green", "Black"]


def test_split_or_colours_splits_on_or() -> None:
    """'Green or Black' continues to be split into two separate colour entries."""
    result = ColourScopeHandler.split_or_colours(["Green or Black"])
    assert result == ["Green", "Black"]


def test_split_or_colours_no_split_for_plain_colour() -> None:
    """Colours without 'and'/'or' are left unchanged."""
    result = ColourScopeHandler.split_or_colours(["Red", "Blue"])
    assert result == ["Red", "Blue"]


def test_split_or_colours_multiple_items_with_and() -> None:
    """Each colour entry is split independently."""
    result = ColourScopeHandler.split_or_colours(["Red", "Green and Black"])
    assert result == ["Red", "Green", "Black"]


# ── New fixes ─────────────────────────────────────────────────────────────────


# Fix: split_or_colours must not split inside parentheses (depth-aware)

def test_split_or_colours_no_split_inside_parens() -> None:
    """'and' inside parentheses is not treated as a colour separator."""
    result = ColourScopeHandler.split_or_colours(
        ["Blue (1964 United States and Mexican Grands Prix)"],
    )
    assert result == ["Blue (1964 United States and Mexican Grands Prix)"]


def test_split_or_colours_splits_outside_parens_only() -> None:
    """'and' at depth 0 still splits, even when parens are present elsewhere."""
    result = ColourScopeHandler.split_or_colours(
        ["Red and Blue (Monaco Grand Prix)"],
    )
    assert result == ["Red", "Blue (Monaco Grand Prix)"]


def test_colour_grand_prix_scope_cleans_colour_name() -> None:
    """colour_grand_prix_scope strips the GP annotation from the cleaned colour."""
    scope, cleaned = ColourScopeHandler.colour_grand_prix_scope(
        "Blue (United States and Mexican Grands Prix)",
    )
    assert scope is not None
    assert cleaned == "Blue"


def test_colour_grand_prix_scope_handles_grands_prix_plural() -> None:
    """colour_grand_prix_scope handles plural 'Grands Prix' correctly."""
    scope, cleaned = ColourScopeHandler.colour_grand_prix_scope(
        "Blue (1964 United States and Mexican Grands Prix)",
    )
    assert scope is not None
    assert scope["type"] == "only"
    gp_names = [e["text"] for e in scope["grand_prix"]]
    assert "United States Grand Prix" in gp_names
    assert "Mexican Grand Prix" in gp_names
    assert cleaned == "Blue"


# Fix: ColourListColumn – <br> as separator

def test_colour_list_column_br_as_separator() -> None:
    """<br> inside a colour cell is treated as a value separator."""
    from scrapers.sponsorship_liveries.columns.colour import ColourListColumn
    col = ColourListColumn()
    cell = BeautifulSoup("<td>White<br>Dark Blue and White</td>", "html.parser").find("td")
    ctx = ColumnContext(
        header="Main colour(s)",
        key="main_colours",
        raw_text="White Dark Blue and White",
        clean_text="White Dark Blue and White",
        links=[],
        cell=cell,
        base_url="https://en.wikipedia.org",
    )
    result = col.parse(ctx)
    # <br> splits into "White" and "Dark Blue and White" segments;
    # the "and" split happens later via split_or_colours
    assert "White" in result
    assert "Dark Blue and White" in result
    assert result.index("White") < result.index("Dark Blue and White")


# Fix: ColourListColumn – <p> as separator

def test_colour_list_column_p_as_separator() -> None:
    """<p> boundary inside a colour cell is treated as a value separator."""
    from scrapers.sponsorship_liveries.columns.colour import ColourListColumn
    col = ColourListColumn()
    cell = BeautifulSoup(
        "<td>Black and Green\n<p>White and Blue\n</p></td>", "html.parser",
    ).find("td")
    ctx = ColumnContext(
        header="Main colour(s)",
        key="main_colours",
        raw_text="Black and Green White and Blue",
        clean_text="Black and Green White and Blue",
        links=[],
        cell=cell,
        base_url="https://en.wikipedia.org",
    )
    result = col.parse(ctx)
    assert "Black and Green" in result
    assert "White and Blue" in result


# Fix: ColourListColumn – skip parenthetical-only <p>

def test_colour_list_column_skips_parenthetical_p() -> None:
    """A <p> that consists entirely of parenthetical text is ignored."""
    from scrapers.sponsorship_liveries.columns.colour import ColourListColumn
    col = ColourListColumn()
    html = (
        "<td>White and Yellow\n"
        "<p>(Image of a woman holding a box of Rizla+. cigarette papers)\n</p>"
        "</td>"
    )
    cell = BeautifulSoup(html, "html.parser").find("td")
    ctx = ColumnContext(
        header="Additional colour(s)",
        key="additional_colours",
        raw_text="White and Yellow (Image of a woman holding a box of Rizla+. cigarette papers)",
        clean_text="White and Yellow (Image of a woman holding a box of Rizla+. cigarette papers)",
        links=[],
        cell=cell,
        base_url="https://en.wikipedia.org",
    )
    result = col.parse(ctx)
    # The parenthetical image description should not appear in the colours
    assert result == ["White and Yellow"]
    assert not any("Image" in c for c in result)


# Fix: SeasonService – "YYYY to YYYY" range support

def test_season_service_to_range() -> None:
    """'1997 to 1999' is parsed as a full year range."""
    from models.services.season_service import SeasonService
    result = SeasonService.parse_seasons("1997 to 1999")
    years = [e["year"] for e in result]
    assert years == [1997, 1998, 1999]


def test_season_service_to_range_mixed_with_comma() -> None:
    """'1997 to 1999, 2001' is parsed correctly."""
    from models.services.season_service import SeasonService
    result = SeasonService.parse_seasons("1997 to 1999, 2001")
    years = [e["year"] for e in result]
    assert years == [1997, 1998, 1999, 2001]


def test_season_service_to_range_case_insensitive() -> None:
    """'1997 TO 1999' (uppercase) is also parsed correctly."""
    from models.services.season_service import SeasonService
    result = SeasonService.parse_seasons("1997 TO 1999")
    years = [e["year"] for e in result]
    assert years == [1997, 1998, 1999]


# ── Fix: Possessive 's grouping – "and"-joined colour groups ─────────────────


def test_possessive_group_not_split_on_and() -> None:
    """'Green and White (Pescarolo's car)' must NOT be split into two colours."""
    result = ColourScopeHandler.split_or_colours(["Green and White (Pescarolo's car)"])
    assert result == ["Green and White (Pescarolo's car)"]


def test_possessive_group_two_drivers() -> None:
    """Full Matra case: two colour groups with possessive annotations."""
    from scrapers.base.helpers.text_normalization import split_delimited_text
    text = "Green and White (Pescarolo's car), White and Red (Beltoise's car)"
    parts = split_delimited_text(text)
    result = ColourScopeHandler.split_or_colours(parts)
    assert result == [
        "Green and White (Pescarolo's car)",
        "White and Red (Beltoise's car)",
    ]


def test_possessive_group_single_colour_not_affected() -> None:
    """A single colour with possessive paren keeps its paren and is not split."""
    result = ColourScopeHandler.split_or_colours(["Red (Beltoise's car)"])
    assert result == ["Red (Beltoise's car)"]


def test_non_possessive_paren_still_splits() -> None:
    """'Green and White (1965)' WITHOUT possessive 's still splits into two colours."""
    result = ColourScopeHandler.split_or_colours(["Green and White (1965)"])
    assert "Green" in result and "White (1965)" in result


# ── Fix: livery_principal_sponsors year-range filtering ──────────────────────


def test_livery_principal_sponsors_year_filter() -> None:
    """livery_principal_sponsors is correctly filtered per expanded season year."""
    from scrapers.sponsorship_liveries.parsers.record_splitter import SponsorshipRecordSplitter

    sponsors = [
        {"text": "OKX", "url": "https://en.wikipedia.org/wiki/OKX"},
        {
            "text": "Google Chrome",
            "url": "https://en.wikipedia.org/wiki/Google_Chrome",
            "params": ["2024-2025"],
        },
        {
            "text": "Google Gemini",
            "url": "https://en.wikipedia.org/wiki/Gemini_(chatbot)",
            "params": ["2025-2026"],
        },
        {"text": "Mastercard", "url": "https://en.wikipedia.org/wiki/Mastercard"},
    ]
    record = {
        "season": [
            {"year": 2024, "url": "https://en.wikipedia.org/wiki/2024_Formula_One_World_Championship"},
            {"year": 2025, "url": "https://en.wikipedia.org/wiki/2025_Formula_One_World_Championship"},
            {"year": 2026, "url": "https://en.wikipedia.org/wiki/2026_Formula_One_World_Championship"},
        ],
        "main_colours": ["Orange", "Black"],
        "livery_principal_sponsors": sponsors,
    }
    splitter = SponsorshipRecordSplitter()
    result = splitter.split_record_by_season(record)

    assert len(result) == 3

    by_year = {r["season"][0]["year"]: r for r in result}

    texts_2024 = [s.get("text") for s in by_year[2024]["livery_principal_sponsors"]]
    assert texts_2024 == ["OKX", "Google Chrome", "Mastercard"]

    texts_2025 = [s.get("text") for s in by_year[2025]["livery_principal_sponsors"]]
    assert texts_2025 == ["OKX", "Google Chrome", "Google Gemini", "Mastercard"]

    texts_2026 = [s.get("text") for s in by_year[2026]["livery_principal_sponsors"]]
    assert texts_2026 == ["OKX", "Google Gemini", "Mastercard"]


# ── Possessive 's → driver record splitting ───────────────────────────────────


def test_has_possessive_colour_groups_true() -> None:
    """has_possessive_colour_groups detects a possessive group."""
    assert ColourScopeHandler.has_possessive_colour_groups(
        ["Green and White (Pescarolo's car)"],
    )


def test_has_possessive_colour_groups_false_plain() -> None:
    """has_possessive_colour_groups returns False for plain colour names."""
    assert not ColourScopeHandler.has_possessive_colour_groups(["Green", "White"])


def test_has_possessive_colour_groups_false_year() -> None:
    """has_possessive_colour_groups returns False when paren contains only a year."""
    assert not ColourScopeHandler.has_possessive_colour_groups(["Green (1965)"])


def test_extract_possessive_colour_groups_two_drivers() -> None:
    """extract_possessive_colour_groups correctly extracts driver names and colours."""
    groups = ColourScopeHandler.extract_possessive_colour_groups(
        ["Green and White (Pescarolo's car)", "White and Red (Beltoise's car)"],
    )
    assert groups == [
        ("Pescarolo", ["Green", "White"]),
        ("Beltoise", ["White", "Red"]),
    ]


def test_extract_possessive_colour_groups_mixed() -> None:
    """Non-possessive items are returned with driver_name=None."""
    groups = ColourScopeHandler.extract_possessive_colour_groups(
        ["Blue", "Green and White (Pescarolo's car)"],
    )
    assert groups == [
        (None, ["Blue"]),
        ("Pescarolo", ["Green", "White"]),
    ]


def test_split_record_by_season_matra_case() -> None:
    """Full Matra integration: possessive groups produce two driver records."""
    from scrapers.base.helpers.text_normalization import split_delimited_text
    from scrapers.sponsorship_liveries.parsers.record_splitter import SponsorshipRecordSplitter

    text = "Green and White (Pescarolo's car), White and Red (Beltoise's car)"
    colour_list = split_delimited_text(text)

    record = {
        "season": [
            {"year": 1970, "url": "https://en.wikipedia.org/wiki/1970_Formula_One_World_Championship"},
            {"year": 1971, "url": "https://en.wikipedia.org/wiki/1971_Formula_One_World_Championship"},
            {"year": 1972, "url": "https://en.wikipedia.org/wiki/1972_Formula_One_World_Championship"},
        ],
        "main_colours": ["Blue"],
        "additional_colours": colour_list,
        "livery_sponsors": ["Matra-Simca"],
    }

    splitter = SponsorshipRecordSplitter()
    result = splitter.split_record_by_season(record)

    assert len(result) == 2

    by_driver = {r["driver"][0]["text"]: r for r in result}

    pescarolo = by_driver["Pescarolo"]
    assert pescarolo["main_colours"] == ["Blue"]
    assert pescarolo["additional_colours"] == ["Green", "White"]
    assert len(pescarolo["season"]) == 3

    beltoise = by_driver["Beltoise"]
    assert beltoise["main_colours"] == ["Blue"]
    assert beltoise["additional_colours"] == ["White", "Red"]
    assert len(beltoise["season"]) == 3


def test_split_record_by_season_possessive_with_common_colours() -> None:
    """Common (non-possessive) colours are shared across all driver records."""
    from scrapers.sponsorship_liveries.parsers.record_splitter import SponsorshipRecordSplitter

    record = {
        "season": [{"year": 1970}],
        "main_colours": ["Blue"],
        "additional_colours": [
            "Yellow",
            "Green and White (Pescarolo's car)",
            "White and Red (Beltoise's car)",
        ],
    }

    splitter = SponsorshipRecordSplitter()
    result = splitter.split_record_by_season(record)

    assert len(result) == 2
    by_driver = {r["driver"][0]["text"]: r for r in result}
    # Each driver gets their colours + the shared "Yellow"
    assert by_driver["Pescarolo"]["additional_colours"] == ["Green", "White", "Yellow"]
    assert by_driver["Beltoise"]["additional_colours"] == ["White", "Red", "Yellow"]
