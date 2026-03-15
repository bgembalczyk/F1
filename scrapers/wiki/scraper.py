from typing import Any

from bs4 import BeautifulSoup

from scrapers.wiki.parsers.body_content import BodyContentParser
from scrapers.wiki.parsers.header import HeaderParser


class WikiScraper:
    """Scraper artykułów Wikipedii.

    Pobiera kod HTML strony Wikipedii na podstawie podanego URL,
    a następnie parsuje go przy użyciu:
    - HeaderParser – przetwarza nagłówek strony
      (<header class="mw-body-header vector-page-titlebar no-font-mode-scale">)
    - BodyContentParser – przetwarza główną treść strony
      (<div id="bodyContent">)

    Pobieranie HTML odbywa się za pośrednictwem http_client.
    Po stronie klienta podejmowana jest decyzja, czy dane są pobierane
    bezpośrednio z sieci, czy zwracane z cache.

    Użycie:
        from infrastructure.http_client.http_client import HttpClient
        from scrapers.wiki.scraper import WikiScraper

        http_client = HttpClient(...)
        scraper = WikiScraper(http_client=http_client)
        result = scraper.scrape("https://en.wikipedia.org/wiki/Lewis_Hamilton")
    """

    def __init__(
        self,
        http_client: Any,
        *,
        header_parser: HeaderParser | None = None,
        body_content_parser: BodyContentParser | None = None,
    ) -> None:
        """Inicjalizuje WikiScraper.

        Args:
            http_client: Klient HTTP z metodą get_text(url) używany do pobierania HTML.
                Po stronie klienta leży decyzja o pobieraniu bezpośrednim lub z cache.
            header_parser: Parser nagłówka strony. Domyślnie tworzy nowy HeaderParser.
            body_content_parser: Parser treści strony. Domyślnie tworzy nowy
                BodyContentParser.
        """
        self.http_client = http_client
        self.header_parser = header_parser or HeaderParser()
        self.body_content_parser = body_content_parser or BodyContentParser()

    def scrape(self, url: str) -> dict[str, Any]:
        """Pobiera i parsuje artykuł Wikipedii pod podanym adresem URL.

        Args:
            url: Adres URL artykułu Wikipedii.

        Returns:
            Słownik z:
            - 'url': podany adres URL
            - 'header': wyniki parsowania nagłówka strony
            - 'body_content': wyniki parsowania treści strony
        """
        html = self._fetch(url)
        soup = BeautifulSoup(html, "html.parser")
        return self._parse(url, soup)

    def _fetch(self, url: str) -> str:
        """Pobiera kod HTML strony za pomocą http_client.

        Args:
            url: Adres URL do pobrania.

        Returns:
            Kod HTML strony jako string.
        """
        return self.http_client.get_text(url)

    def _parse(self, url: str, soup: BeautifulSoup) -> dict[str, Any]:
        """Parsuje sparsowaną stronę HTML.

        Args:
            url: Adres URL (dołączany do wyniku).
            soup: Sparsowany HTML jako obiekt BeautifulSoup.

        Returns:
            Słownik z wynikami parsowania nagłówka i treści.
        """
        result: dict[str, Any] = {
            "url": url,
            "header": None,
            "body_content": None,
        }

        header_el = HeaderParser.find_header(soup)
        if header_el is not None:
            result["header"] = self.header_parser.parse(header_el)

        body_content_el = BodyContentParser.find_body_content(soup)
        if body_content_el is not None:
            result["body_content"] = self.body_content_parser.parse(body_content_el)

        return result
