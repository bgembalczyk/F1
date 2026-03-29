from bs4 import BeautifulSoup
from bs4 import Tag

from scrapers.wiki.parsers.base import WikiParser
from scrapers.wiki.parsers.constants import HEADER_CLASS
from scrapers.wiki.parsers.constants import HEADER_TAG
from scrapers.wiki.parsers.types import HeaderParsedData


class HeaderParser(WikiParser[HeaderParsedData]):
    """Parser nagłówka strony Wikipedii.

    Przetwarza element:
    <header class="mw-body-header vector-page-titlebar no-font-mode-scale">
    """

    def parse(self, element: Tag) -> HeaderParsedData:
        """Parsuje nagłówek strony Wikipedii.

        Args:
            element: Element <header class="mw-body-header...">.

        Returns:
            Słownik z tytułem strony i ewentualnymi dodatkowymi danymi.
        """
        title_tag = element.find(
            ["h1", "span"],
            class_=lambda x: x
            and "mw-page-title" in (x if isinstance(x, list) else x.split()),
        )
        if title_tag is None:
            title_tag = element.find("h1")

        title = title_tag.get_text(" ", strip=True) if title_tag else None
        return {"title": title}

    @staticmethod
    def find_header(soup: BeautifulSoup) -> Tag | None:
        """Znajduje element header z klasą mw-body-header w podanym soup.

        Args:
            soup: Obiekt BeautifulSoup całej strony.

        Returns:
            Znaleziony element header lub None.
        """
        return soup.find(
            HEADER_TAG,
            class_=lambda x: x
            and HEADER_CLASS in (x if isinstance(x, list) else x.split()),
        )
