from typing import Any

from bs4 import Tag

from scrapers.wiki.parsers.base import WikiParser


class CategoryLinksParser(WikiParser):
    """Parser linków do kategorii Wikipedii.

    Przetwarza div z id="catlinks".
    """

    def parse(self, element: Tag) -> dict[str, Any]:
        """Parsuje sekcję linków do kategorii.

        Args:
            element: Div z id="catlinks".

        Returns:
            Słownik z listą kategorii i ich linkami.
        """
        categories: list[dict[str, Any]] = []
        for catlinks_div in element.find_all("div", id=True):
            cat_label = catlinks_div.find("a")
            cat_name = cat_label.get_text(" ", strip=True) if cat_label else None
            links = [
                {"text": a.get_text(" ", strip=True), "href": a.get("href")}
                for a in catlinks_div.find_all("a")[1:]
                if a.get("href")
            ]
            if links:
                categories.append({"category": cat_name, "links": links})

        if not categories:
            links = [
                {"text": a.get_text(" ", strip=True), "href": a.get("href")}
                for a in element.find_all("a")
                if a.get("href")
            ]
            categories = [{"category": None, "links": links}]

        return {"categories": categories}
