from typing import TYPE_CHECKING
from typing import Any

from bs4 import BeautifulSoup

from scrapers.base.abc import ABCScraper
from scrapers.base.helpers.http import init_scraper_options
from scrapers.base.options import ScraperOptions
from scrapers.wiki.parsers.body_content import BodyContentParser
from scrapers.wiki.parsers.elements.parsers import WikiElementParsers
from scrapers.wiki.parsers.elements.parsers import build_default_wiki_element_parsers
from scrapers.wiki.parsers.header import HeaderParser
from scrapers.wiki.parsers.sections.sub_sub_sub_section import WikiElementParserMixin

if TYPE_CHECKING:
    from scrapers.wiki.parsers.sections.section import SectionParser


class WikiScraper(WikiElementParserMixin, ABCScraper):
    """Bazowy scraper artykułów Wikipedii.

    Dziedziczy z ABCScraper, zapewniając pełen pipeline:
    download → parse → normalize → transform → validate → export.

    Klasa ta obsługuje specyficzne dla Wikipedii parsery stron:
    - HeaderParser - przetwarza nagłówek strony
      (<header class="mw-body-header vector-page-titlebar no-font-mode-scale">)
    - BodyContentParser - przetwarza główną treść strony
      (<div id="bodyContent">)

    Pobieranie HTML odbywa się za pośrednictwem source_adapter (HtmlFetcher),
    który po swojej stronie decyduje, czy dane są pobierane bezpośrednio z sieci,
    czy zwracane z cache.

    ListScrapery i SingleScrapery dziedziczą po WikiScraperze i nadpisują
    metodę _parse_soup, korzystając ze swoich wyspecjalizowanych parserów.

    Użycie jako samodzielny scraper artykułu Wikipedii:
        scraper = WikiScraper()
        result = scraper.scrape("https://en.wikipedia.org/wiki/Lewis_Hamilton")
    """

    #: URL artykułu Wikipedii (ustawiany dynamicznie lub przez podklasy)
    url: str = ""
    scraper_kind: str = "single"

    def __init__(
        self,
        *,
        options: ScraperOptions | None = None,
        header_parser: HeaderParser | None = None,
        body_content_parser: BodyContentParser | None = None,
        element_parsers: WikiElementParsers | None = None,
    ) -> None:
        """Inicjalizuje WikiScraper.

        Args:
            options: Opcje scrapera (HTTP, cache, eksport itp.).
                Domyślnie tworzy nowe ScraperOptions.
            header_parser: Parser nagłówka strony. Domyślnie tworzy nowy HeaderParser.
            body_content_parser: Parser treści strony. Domyślnie tworzy nowy
                BodyContentParser.
        """
        resolved_element_parsers = element_parsers or build_default_wiki_element_parsers()
        WikiElementParserMixin.__init__(
            self,
            element_parsers=resolved_element_parsers,
        )
        options = init_scraper_options(options)
        ABCScraper.__init__(self, options=options)

        self.header_parser = header_parser or HeaderParser()
        self.body_content_parser = body_content_parser or BodyContentParser(
            element_parsers=resolved_element_parsers,
        )
        self.section_parser: SectionParser = (
            self.body_content_parser.content_text_parser.section_parser
        )

    def scrape(self, url: str) -> dict[str, Any]:
        """Pobiera i parsuje artykuł Wikipedii pod podanym adresem URL.

        Wygodna metoda opakowująca pełny pipeline ABCScrapera.

        Args:
            url: Adres URL artykułu Wikipedii.

        Returns:
            Słownik z:
            - 'url': podany adres URL
            - 'header': wyniki parsowania nagłówka strony
            - 'body_content': wyniki parsowania treści strony
            Lub pusty słownik, gdy nie udało się pobrać/sparsować.
        """
        self.url = url
        records = self.fetch()
        return records[0] if records else {}

    def _parse_soup(self, soup: BeautifulSoup) -> list[dict[str, Any]]:
        """Domyślne parsowanie strony Wikipedii.

        Korzysta z HeaderParser i BodyContentParser.
        Podklasy (ListScrapery, SingleScrapery) nadpisują tę metodę.

        Args:
            soup: Sparsowany HTML jako obiekt BeautifulSoup.

        Returns:
            Lista z jednym słownikiem zawierającym dane ze strony.
        """
        result: dict[str, Any] = {
            "url": self.url,
            "header": None,
            "body_content": None,
        }

        header_el = HeaderParser.find_header(soup)
        if header_el is not None:
            result["header"] = self.header_parser.parse(header_el)

        body_content_el = BodyContentParser.find_body_content(soup)
        if body_content_el is not None:
            result["body_content"] = self.body_content_parser.parse(body_content_el)

        return [result]
