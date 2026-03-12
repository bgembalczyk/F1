"""Tests for sponsorship liveries column fixes."""
from bs4 import BeautifulSoup

from scrapers.base.table.columns.context import ColumnContext
from scrapers.sponsorship_liveries.columns.seasons import SponsorshipSeasonsColumn
from scrapers.sponsorship_liveries.columns.sponsor import SponsorColumn


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
    """When parenthetical contains 'car', linked item is stored under 'car'."""
    col = SponsorshipSeasonsColumn()
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
    """Without 'car' keyword, linked item is stored under 'driver' as before."""
    col = SponsorshipSeasonsColumn()
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
