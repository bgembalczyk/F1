from bs4 import Tag

from scrapers.wiki.parsers.base import WikiParser
from scrapers.wiki.parsers.types import CategoryGroup
from scrapers.wiki.parsers.types import CategoryLinksParsedData


class CategoryLinksParser(WikiParser[CategoryLinksParsedData]):
    """Parser linków do kategorii Wikipedii.

    Przetwarza div z id="catlinks".
    """

    def parse(self, element: Tag) -> CategoryLinksParsedData:
        """Parsuje sekcję linków do kategorii.

        Args:
            element: Div z id="catlinks".

        Returns:
            Słownik z listą kategorii i ich linkami.
        """
        categories: list[CategoryGroup] = []
        for catlinks_div in element.find_all("div", id=True):
            cat_label = catlinks_div.find("a")
            cat_name = cat_label.get_text(" ", strip=True) if cat_label else None
            links = []
            for anchor in catlinks_div.find_all("a")[1:]:
                href = anchor.get("href")
                if isinstance(href, str):
                    links.append(
                        {"text": anchor.get_text(" ", strip=True), "href": href},
                    )
            if links:
                categories.append({"category": cat_name, "links": links})

        if not categories:
            links = []
            for anchor in element.find_all("a"):
                href = anchor.get("href")
                if isinstance(href, str):
                    links.append(
                        {"text": anchor.get_text(" ", strip=True), "href": href},
                    )
            categories = [{"category": None, "links": links}]

        return {"categories": categories}
