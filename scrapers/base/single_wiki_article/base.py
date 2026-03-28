from abc import ABC
from abc import abstractmethod
from typing import Any

from bs4 import BeautifulSoup

from scrapers.base.helpers.http import init_scraper_options
from scrapers.base.options import ScraperOptions
from scrapers.base.post_processors import RecordPostProcessor
from scrapers.wiki.scraper import WikiScraper


class SingleWikiArticleScraperBase(WikiScraper, ABC):
    """Wspólna baza dla scraperów pojedynczych artykułów Wikipedii.

    Kontrakt etapów pipeline i hooków domenowych:
    1. ``_prepare_article_soup(soup)`` — opcjonalne zawężenie/normalizacja HTML.
    2. ``_before_payload_build(soup)`` — opcjonalny hook wykonywany przed
       budowaniem payloadów.
    3. ``_build_infobox_payload(soup)`` / ``_build_tables_payload(soup)`` /
       ``_build_sections_payload(soup)`` — etapowe budowanie danych.
    4. ``_assemble_record(...)`` — złożenie finalnego rekordu domenowego.
    5. ``_after_record_assembled(record, soup)`` — opcjonalny hook końcowy
       pozwalający uzupełnić/zmodyfikować rekord.

    Pozostałe hooki kontrolne:
    - ``_build_post_processor()``: zwraca wymagany post-processor domenowy
      lub ``None`` gdy domena go nie wymaga.
    - ``_should_parse_article(soup)``: pozwala pominąć artykuły niespełniające
      warunków domenowych.
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
        return self._run_record_pipeline(soup)

    def _run_record_pipeline(self, soup: BeautifulSoup) -> dict[str, Any]:
        """Uruchom pełny pipeline budowy rekordu na podstawie jednego ``soup``."""
        self._before_payload_build(soup)
        record = self._assemble_record(
            soup=soup,
            infobox_payload=self._build_infobox_payload(soup),
            tables_payload=self._build_tables_payload(soup),
            sections_payload=self._build_sections_payload(soup),
        )
        return self._after_record_assembled(record, soup)

    def _before_payload_build(self, soup: BeautifulSoup) -> None:
        """Opcjonalny hook wywoływany przed budowaniem payloadów."""
        _ = soup

    def _after_record_assembled(
        self,
        record: dict[str, Any],
        soup: BeautifulSoup,
    ) -> dict[str, Any]:
        """Opcjonalny hook wywoływany po ``_assemble_record``."""
        _ = soup
        return record

    def _build_infobox_payload(self, soup: BeautifulSoup) -> Any:
        """Build normalized infobox payload used by ``_assemble_record``."""
        _ = soup
        return []

    def _build_tables_payload(self, soup: BeautifulSoup) -> Any:
        """Build normalized table payload used by ``_assemble_record``."""
        _ = soup
        return []

    def _build_sections_payload(self, soup: BeautifulSoup) -> Any:
        """Build normalized section payload used by ``_assemble_record``."""
        _ = soup
        return []

    @abstractmethod
    def _assemble_record(
        self,
        *,
        soup: BeautifulSoup,
        infobox_payload: Any,
        tables_payload: Any,
        sections_payload: Any,
    ) -> dict[str, Any]:
        """Compose final domain record from template-method payload hooks."""
