# ruff: noqa: E501, PLR2004
import pytest
from bs4 import BeautifulSoup

from scrapers.base.table.columns.context import ColumnContext
from scrapers.seasons.columns.calendar_circuit import CalendarCircuitColumn


def _ctx(html: str, links: list[dict] | None = None, clean_text: str | None = None) -> ColumnContext:
    cell = BeautifulSoup(f"<td>{html}</td>", "html.parser").find("td")
    text = cell.get_text(" ", strip=True)
    return ColumnContext(
        header="Circuit",
        key="circuit",
        raw_text=text,
        clean_text=clean_text if clean_text is not None else text,
        links=links or [],
        cell=cell,
        base_url="https://en.wikipedia.org",
        model_fields=None,
    )


def test_calendar_circuit_no_links_with_text_returns_circuit_dict() -> None:
    col = CalendarCircuitColumn()
    result = col.parse(_ctx("Silverstone Circuit", links=[]))
    assert result == {"circuit": {"text": "Silverstone Circuit", "url": None}}


def test_calendar_circuit_no_links_no_text_returns_none() -> None:
    col = CalendarCircuitColumn()
    result = col.parse(_ctx("", links=[], clean_text=""))
    assert result is None


def test_calendar_circuit_one_link_returns_circuit_only() -> None:
    links = [{"text": "Silverstone", "url": "https://en.wikipedia.org/wiki/Silverstone_Circuit"}]
    col = CalendarCircuitColumn()
    result = col.parse(_ctx("<a>Silverstone</a>", links=links))
    assert "circuit" in result
    assert "location" not in result
    assert result["circuit"]["text"] == "Silverstone"


def test_calendar_circuit_two_links_returns_circuit_and_location() -> None:
    links = [
        {"text": "Silverstone", "url": "https://en.wikipedia.org/wiki/Silverstone_Circuit"},
        {"text": "Northamptonshire", "url": "https://en.wikipedia.org/wiki/Northamptonshire"},
    ]
    col = CalendarCircuitColumn()
    result = col.parse(_ctx("<a>Silverstone</a> <a>Northamptonshire</a>", links=links))
    assert result["circuit"]["text"] == "Silverstone"
    assert result["location"]["text"] == "Northamptonshire"
