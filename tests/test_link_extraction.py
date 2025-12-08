import pytest

bs4 = pytest.importorskip("bs4")
from bs4 import BeautifulSoup

from scrapers.base.helpers.utils import extract_links_from_cell
from scrapers.base.infobox.scraper import WikipediaInfoboxScraper


def _full_url(href: str | None) -> str | None:
    if not href:
        return None
    if href.startswith("/"):
        return f"https://example.com{href}"
    return href


def _td(html: str):
    soup = BeautifulSoup(html, "html.parser")
    return soup.find("td")


def test_extract_links_from_cell_handles_references_and_anchors():
    td = _td(
        """
        <td>
            <a href="#cite_note-1" class="reference">[1]</a>
            <a href="#local">Local section</a>
            <a href="/wiki/Example">Example</a>
        </td>
        """
    )

    links = extract_links_from_cell(td, full_url=_full_url)

    assert links == [
        {"text": "Local section", "url": "#local"},
        {"text": "Example", "url": "https://example.com/wiki/Example"},
    ]


def test_infobox_extract_links_uses_reference_helper():
    scraper = WikipediaInfoboxScraper()
    td = _td(
        """
        <td>
            <a href="#cite_note-1" class="reference">[1]</a>
            <a href="#local">Local section</a>
            <a href="/wiki/Example">Example</a>
        </td>
        """
    )

    links = scraper._extract_links(td)

    assert links == [{"text": "Example", "url": "https://en.wikipedia.org/wiki/Example"}]
