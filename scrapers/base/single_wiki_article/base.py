from abc import ABC
from abc import abstractmethod
from typing import Any

from scrapers.base.payloads import InfoboxPayload
from scrapers.base.payloads import SectionsPayload
from scrapers.base.payloads import TablesPayload

from bs4 import BeautifulSoup

from scrapers.base.helpers.http import init_scraper_options
from scrapers.base.options import ScraperOptions
from scrapers.base.post_processors import RecordPostProcessor
from scrapers.wiki.scraper import WikiScraper


class SingleWikiArticleScraperBase(WikiScraper, ABC):
    """Wspólna baza dla scraperów pojedynczych artykułów Wikipedii.

    Kontrakt hooków dla podklas:
    - ``_build_post_processor()``: zwraca wymagany post-processor domenowy
      lub ``None`` gdy domena go nie wymaga.
    - ``_should_parse_article(soup)``: pozwala pominąć artykuły niespełniające
      warunków domenowych.
    - ``_prepare_article_soup(soup)``: pozwala wybrać część artykułu przed
      uruchomieniem parsera domenowego.
    - ``_build_infobox_payload(soup)`` / ``_build_tables_payload(soup)`` /
      ``_build_sections_payload(soup)``: budują składowe rekordu.
    - ``_assemble_record(...)``: składa finalny rekord domenowy.
    """

    def __init__(
        self,
        *,
        options: ScraperOptions | None = None,
        include_urls: bool = True,
    ) -> None:
        resolved_options = init_scraper_options(options, include_urls=include_urls)
        policy = self.get_http_policy(resolved_options)
        resolved_options.with_fetcher(policy=policy)

        post_processor = self._build_post_processor()
        if post_processor is not None:
            resolved_options.post_processors.append(post_processor)

        super().__init__(options=resolved_options)
        self.url: str = ""
        self._options = resolved_options
        self.policy = self.http_policy
        self.debug_dir = resolved_options.debug_dir

    def _build_post_processor(self) -> RecordPostProcessor | None:
        """Zwróć post-processor domenowy dodawany podczas inicjalizacji."""
        return None

    def fetch_by_url(self, url: str) -> list[dict[str, Any]]:
        """Pobiera artykuł po URL i zapisuje go w ``self.url`` przed ``fetch()``."""
        self.url = url
        return super().fetch()

    def parse(self, soup: BeautifulSoup) -> list[dict[str, Any]]:
        if not self._should_parse_article(soup):
            return []

        working_soup = self._prepare_article_soup(soup)
        if self.parser is not None:
            return self.parser.parse(working_soup)
        return self._parse_soup(working_soup)

    def _parse_soup(self, soup: BeautifulSoup) -> list[dict[str, Any]]:
        return [self._build_article_record(soup)]

    def _should_parse_article(self, soup: BeautifulSoup) -> bool:
        """Pozwala pominąć artykuł przed uruchomieniem parsera domenowego."""
        _ = soup
        return True

    def _prepare_article_soup(self, soup: BeautifulSoup) -> BeautifulSoup:
        """Pozwala przygotować wycinek artykułu używany dalej przez hooki."""
        return soup

    def _build_article_record(self, soup: BeautifulSoup) -> dict[str, Any]:
        return self._assemble_record(
            soup=soup,
            infobox_payload=self._build_infobox_payload(soup),
            tables_payload=self._build_tables_payload(soup),
            sections_payload=self._build_sections_payload(soup),
        )

    def _build_infobox_payload(self, soup: BeautifulSoup) -> InfoboxPayload:
        """Build normalized infobox payload used by ``_assemble_record``."""
        _ = soup
        return InfoboxPayload(data=[])

    def _build_tables_payload(self, soup: BeautifulSoup) -> TablesPayload:
        """Build normalized table payload used by ``_assemble_record``."""
        _ = soup
        return TablesPayload(data=[])

    def _build_sections_payload(self, soup: BeautifulSoup) -> SectionsPayload:
        """Build normalized section payload used by ``_assemble_record``."""
        _ = soup
        return SectionsPayload(data=[])

    @abstractmethod
    def _assemble_record(
        self,
        *,
        soup: BeautifulSoup,
        infobox_payload: InfoboxPayload,
        tables_payload: TablesPayload,
        sections_payload: SectionsPayload,
    ) -> dict[str, Any]:
        """Compose final domain record from template-method payload hooks."""
