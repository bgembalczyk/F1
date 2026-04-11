from bs4 import Tag

from models.data.parsed.nav_box import NavBoxParsedData
from scrapers.parsers.text_cleaning import extract_text
from scrapers.parsers.wiki.base import WikiParser


class NavBoxParser(WikiParser[Tag, NavBoxParsedData]):
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
