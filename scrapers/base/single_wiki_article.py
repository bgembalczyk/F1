from __future__ import annotations

from abc import ABC
from abc import abstractmethod
from typing import TYPE_CHECKING
from typing import Any

from scrapers.base.helpers.http import init_scraper_options
from scrapers.base.mixins.wiki_sections import WikipediaSectionByIdMixin

if TYPE_CHECKING:
    from bs4 import BeautifulSoup

    from scrapers.base.options import ScraperOptions
    from scrapers.base.post_processors import RecordPostProcessor

from scrapers.base.sections.adapter import SectionAdapter
from scrapers.wiki.scraper import WikiScraper


class SingleWikiArticleScraperBase(WikiScraper, ABC):
    """Wspólna baza dla scraperów pojedynczych artykułów Wikipedii.

    Kontrakt hooków dla podklas:
    - ``_build_post_processor()``: zwraca wymagany post-processor domenowy
      lub ``None`` gdy domena go nie wymaga.
    - ``_parse_soup(soup)``: implementuje logikę domenową i zwraca listę rekordów.
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

    @abstractmethod
    def _build_post_processor(self) -> RecordPostProcessor | None:
        """Zwróć post-processor domenowy dodawany podczas inicjalizacji."""

    def fetch_by_url(self, url: str) -> list[dict[str, Any]]:
        """Pobiera artykuł po URL i zapisuje go w ``self.url`` przed ``fetch()``."""
        self.url = url
        return super().fetch()


class SingleWikiArticleSectionAdapterBase(
    SectionAdapter,
    SingleWikiArticleScraperBase,
    ABC,
):
    """Wariant dla scraperów opartych o ``SectionAdapter``.

    Zapewnia nie-fragmentowe ``fetch_by_url`` (bez rozdzielania ``#section``).
    """

    def fetch_by_url(self, url: str) -> list[dict[str, Any]]:
        return SingleWikiArticleScraperBase.fetch_by_url(self, url)

    def _parse_soup(self, soup: BeautifulSoup) -> list[dict[str, Any]]:
        return [self._build_article_record(soup)]

    def _build_article_record(self, soup: BeautifulSoup) -> dict[str, Any]:
        return self._assemble_record(
            soup=soup,
            infobox_payload=self._build_infobox_payload(soup),
            sections_payload=self._build_sections_payload(soup),
        )

    @abstractmethod
    def _build_infobox_payload(self, soup: BeautifulSoup) -> list[dict[str, Any]]:
        """Build normalized infobox payload used by ``_assemble_record``."""

    @abstractmethod
    def _build_sections_payload(self, soup: BeautifulSoup) -> list[dict[str, Any]]:
        """Build normalized section payload used by ``_assemble_record``."""

    @abstractmethod
    def _assemble_record(
        self,
        *,
        soup: BeautifulSoup,
        infobox_payload: list[dict[str, Any]],
        sections_payload: list[dict[str, Any]],
    ) -> dict[str, Any]:
        """Compose final domain record from template-method payload hooks."""


class SingleWikiArticleSectionByIdBase(
    WikipediaSectionByIdMixin,
    SingleWikiArticleScraperBase,
    ABC,
):
    """Wariant bazy dla scraperów, które używają ``WikipediaSectionByIdMixin``.

    ``fetch_by_url`` pochodzi z mixina i obsługuje URL z fragmentem sekcji.
    """
