# ruff: noqa: E501
"""Colour parsing tests for sponsorship liveries."""

from bs4 import BeautifulSoup

from scrapers.base.table.columns.context import ColumnContext
from scrapers.sponsorship_liveries.parsers.colour_scope import ColourScopeHandler


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


def test_colour_list_column_br_as_separator() -> None:
    """<br> inside a colour cell is treated as a value separator."""
    from scrapers.sponsorship_liveries.columns.colour import ColourListColumn

    col = ColourListColumn()
    cell = BeautifulSoup("<td>White<br>Dark Blue and White</td>", "html.parser").find(
        "td",
    )
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
    assert "White" in result
    assert "Dark Blue and White" in result
    assert result.index("White") < result.index("Dark Blue and White")


def test_colour_list_column_p_as_separator() -> None:
    """<p> boundary inside a colour cell is treated as a value separator."""
    from scrapers.sponsorship_liveries.columns.colour import ColourListColumn

    col = ColourListColumn()
    cell = BeautifulSoup(
        "<td>Black and Green\n<p>White and Blue\n</p></td>",
        "html.parser",
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
    assert result == ["White and Yellow"]
    assert not any("Image" in c for c in result)


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
    assert "Green" in result
    assert "White (1965)" in result


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
