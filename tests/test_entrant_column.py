# ruff: noqa: E501, PLR2004, RUF001, RUF002, RUF003, SLF001, ARG001, ARG002, N802, B017, PT011, PT017, E402, PT001, PLC0415, RUF100
from bs4 import BeautifulSoup

from scrapers.base.table.columns.context import ColumnContext
from scrapers.base.table.columns.types import EntrantColumn


def _ctx_with_cell(html: str, *, links: list[dict] | None = None) -> ColumnContext:
    cell = BeautifulSoup(f"<th>{html}</th>", "html.parser").find("th")
    raw_text = cell.get_text(" ", strip=True)
    return ColumnContext(
        header="Entrant",
        key="entrant",
        raw_text=raw_text,
        clean_text=raw_text,
        links=links or [],
        cell=cell,
        base_url="https://en.wikipedia.org",
    )


def test_entrant_br_inside_link_produces_single_entry() -> None:
    """<br> inside an <a> tag should not split into two entrants."""
    html = (
        '<a href="/wiki/Scuderia_Serenissima" title="Scuderia Serenissima">'
        "Scuderia SSS<br>Republica di Venezia</a>"
    )
    column = EntrantColumn()
    result = column.parse(_ctx_with_cell(html))

    assert len(result) == 1
    assert result[0]["name"] == "Scuderia SSS Republica di Venezia"
    assert len(result[0]["title_sponsors"]) == 1
    assert result[0]["title_sponsors"][0]["text"] == "Scuderia SSS Republica di Venezia"
    assert result[0]["title_sponsors"][0]["url"] == (
        "https://en.wikipedia.org/wiki/Scuderia_Serenissima"
    )


def test_entrant_br_outside_link_produces_two_entries() -> None:
    """<br> outside an <a> tag should still split into separate entrants."""
    html = (
        '<a href="/wiki/Team_A" title="Team A">Team A</a>'
        "<br>"
        '<a href="/wiki/Team_B" title="Team B">Team B</a>'
    )
    column = EntrantColumn()
    result = column.parse(_ctx_with_cell(html))

    assert len(result) == 2
    assert result[0]["name"] == "Team A"
    assert result[1]["name"] == "Team B"
