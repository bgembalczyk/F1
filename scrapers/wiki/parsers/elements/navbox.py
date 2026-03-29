from bs4 import Tag

from scrapers.wiki.parsers.base import WikiParser
from scrapers.wiki.parsers.elements.text_cleaning import extract_text
from scrapers.wiki.parsers.types import NavBoxParsedData


class NavBoxParser(WikiParser[NavBoxParsedData]):
    """Parser navboxów Wikipedii.

    Przetwarza element: <div role="navigation" class="navbox">
    """

    def parse(self, element: Tag) -> NavBoxParsedData:
        """Parsuje navbox HTML.

        Args:
            element: Element <div role="navigation" class="navbox">.

        Returns:
            Słownik z tytułem navboxa i linkami.
        """
        title_tag = element.find(class_="navbox-title")
        title = extract_text(title_tag)
        links = []
        for anchor in element.find_all("a"):
            href = anchor.get("href")
            if isinstance(href, str):
                links.append({"text": extract_text(anchor), "href": href})
        return {"title": title, "links": links}
