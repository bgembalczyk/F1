from typing import Any

from bs4 import BeautifulSoup
from bs4 import Tag

from scrapers.parsers.infobox.wiki_html import WikiInfoboxHtmlParser


class WikiInfoboxParser(WikiInfoboxHtmlParser):
    """Wiki parser for infobox tables (<table class="infobox">).

    Returns plain-text strings for row values (no link expansion).
    """

    def parse_row(self, value: Tag) -> str:  # type: ignore[override]
        return value.get_text(" ", strip=True)

    def parse(self, fragment: BeautifulSoup) -> dict[str, Any]:
        return super().parse(fragment)


__all__ = [
    "WikiInfoboxParser",
]
