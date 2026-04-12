from bs4 import Tag

from scrapers.parsers.infobox.wiki_html import WikiInfoboxHtmlParser


class WikiInfoboxParser(WikiInfoboxHtmlParser):
    """Wiki parser for infobox tables (<table class="infobox">).

    Returns plain-text strings for row values (no link expansion).
    """

    def parse_row(self, value: Tag) -> str:  # type: ignore[override]
        return value.get_text(" ", strip=True)


__all__ = [
    "WikiInfoboxParser",
]
