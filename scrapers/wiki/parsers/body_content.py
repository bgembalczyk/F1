from typing import Any

from bs4 import BeautifulSoup
from bs4 import Tag

from scrapers.wiki.parsers.base import WikiParser
from scrapers.wiki.parsers.category_links import CategoryLinksParser
from scrapers.wiki.parsers.content_text import ContentTextParser
from scrapers.wiki.parsers.elements.parsers import WikiElementParsers


class BodyContentParser(WikiParser[dict[str, Any]]):
    """Parser głównej treści strony Wikipedii.

    Przetwarza div z id="bodyContent". Używa:
    - CategoryLinksParser do obsługi div z id="catlinks"
    - ContentTextParser do obsługi div z id zawierającym 'content-text'
      i klasą zawierającą 'body-content'
    """

    def __init__(
        self,
        *,
        element_parsers: WikiElementParsers | None = None,
    ) -> None:
        self.category_links_parser = CategoryLinksParser()
        self.content_text_parser = ContentTextParser(element_parsers=element_parsers)

    def parse(self, element: Tag) -> dict[str, Any]:
        """Parsuje główną treść strony Wikipedii.

        Args:
            element: Div z id="bodyContent".

        Returns:
            Słownik z kategoriami i treścią artykułu.
        """
        result: dict[str, Any] = {
            "category_links": None,
            "content_text": None,
        }

        catlinks = element.find("div", id="catlinks")
        if catlinks and isinstance(catlinks, Tag):
            result["category_links"] = self.category_links_parser.parse(catlinks)

        content_text = element.find(
            "div",
            id=lambda x: x and "content-text" in x,
            class_=lambda x: (
                x and "body-content" in (x if isinstance(x, list) else x.split())
            ),
        )
        if content_text is None:
            content_text = element.find(
                "div",
                class_=lambda x: (
                    x and "mw-content-ltr" in (x if isinstance(x, list) else x.split())
                ),
            )
        if content_text and isinstance(content_text, Tag):
            result["content_text"] = self.content_text_parser.parse(content_text)

        return result

    @staticmethod
    def find_body_content(soup: BeautifulSoup) -> Tag | None:
        """Znajduje div z id="bodyContent" w podanym soup.

        Args:
            soup: Obiekt BeautifulSoup całej strony.

        Returns:
            Znaleziony div lub None.
        """
        return soup.find("div", id="bodyContent")
