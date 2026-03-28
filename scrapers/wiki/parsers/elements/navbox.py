from typing import Any

from bs4 import Tag

from scrapers.wiki.parsers.base import WikiParser
from scrapers.wiki.parsers.elements.text_cleaning import extract_text


class NavBoxParser(WikiParser):
    """Parser navboxów Wikipedii.

    Przetwarza element: <div role="navigation" class="navbox">
    """

    def parse(self, element: Tag) -> dict[str, Any]:
        """Parsuje navbox HTML.

        Args:
            element: Element <div role="navigation" class="navbox">.

        Returns:
            Słownik z tytułem navboxa i linkami.
        """
        title_tag = element.find(class_="navbox-title")
        title = extract_text(title_tag)
        links = [
            {"text": extract_text(a), "href": a.get("href")}
            for a in element.find_all("a")
            if a.get("href")
        ]
        return {"title": title, "links": links}
