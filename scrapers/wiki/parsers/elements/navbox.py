from typing import Any

from bs4 import Tag

from scrapers.wiki.parsers.base import WikiParser


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
        title = title_tag.get_text(" ", strip=True) if title_tag else None
        links = [
            {"text": a.get_text(" ", strip=True), "href": a.get("href")}
            for a in element.find_all("a")
            if a.get("href")
        ]
        return {"title": title, "links": links}
