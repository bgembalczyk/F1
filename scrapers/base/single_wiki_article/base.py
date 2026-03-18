from abc import ABC
from abc import abstractmethod
from typing import Any

from scrapers.base.helpers.http import init_scraper_options
from scrapers.base.options import ScraperOptions
from scrapers.base.post_processors import RecordPostProcessor
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

