import logging
from typing import Any

from bs4 import BeautifulSoup

from scrapers.base.error_handler import ErrorHandler
from scrapers.base.errors import ScraperError
from scrapers.base.helpers.transformer_utils import apply_transformers_with_factory
from scrapers.base.helpers.transformers import build_transformers
from scrapers.base.html_fetcher import HtmlFetcher
from scrapers.base.infobox.field_mapper import InfoboxFieldMapper
from scrapers.base.infobox.helpers import parse_infobox_from_soup
from scrapers.base.infobox.html_parser import InfoboxHtmlParser
from scrapers.base.logging import get_logger
from scrapers.base.options import ScraperOptions

RecoverableError = (
    AttributeError,
    KeyError,
    LookupError,
    OSError,
    RuntimeError,
    TypeError,
    ValueError,
)


class WikipediaInfoboxScraper:
    """
    Scraper infoboksów z artykułów Wikipedii.

    Użycie:
        scraper = WikipediaInfoboxScraper()
        data = scraper.scrape("https://en.wikipedia.org/wiki/Lewis_Hamilton")
    """

    def __init__(
        self,
        *,
        options: ScraperOptions | None = None,
        fetcher: HtmlFetcher | None = None,
        parser: InfoboxHtmlParser | None = None,
        mapper: InfoboxFieldMapper | None = None,
        run_id: str | None = None,
    ) -> None:
        options = options or ScraperOptions()
        if fetcher is not None:
            options.fetcher = fetcher

        self.fetcher = options.with_fetcher()
        self.timeout = options.to_http_policy().timeout
        self.logger = get_logger(self.__class__.__name__)
        self.parser = parser or InfoboxHtmlParser()
        self.mapper = mapper or InfoboxFieldMapper(logger=self.logger)
        self.record_factory = options.record_factory
        self.debug_dir = options.debug_dir
        self.error_report = options.error_report
        self.run_id = run_id
        self.url: str | None = None
        self.transformers = build_transformers(options.transformers)

    # ------------------------------
    # Public API
    # ------------------------------

    def scrape(self, url: str) -> dict[str, Any]:
        """Pobiera i parsuje infobox z dowolnego artykułu Wikipedii."""
        handler = ErrorHandler(
            logger=logging.getLogger(__name__),
            debug_dir=self.debug_dir,
            error_report_enabled=self.error_report,
            run_id=self.run_id,
        )
        html: str | None = None
        try:
            self.url = url
            html = self._fetch(url)
        except ScraperError as error:
            return self._handle_scrape_error(error, handler=handler)
        except RecoverableError as exc:
            error = handler.wrap_network(exc, url=url)
            return self._handle_scrape_error(error, handler=handler, cause=exc)

        try:
            soup = BeautifulSoup(html, "html.parser")
            raw = parse_infobox_from_soup(self, soup)
            return self._apply_transformers(raw)
        except ScraperError as error:
            return self._handle_scrape_error(error, handler=handler)
        except RecoverableError as exc:
            error = handler.wrap_parse(exc, url=url)
            return self._handle_scrape_error(error, handler=handler, cause=exc)

    def apply_record_factory(self, record: dict[str, Any]) -> Any:
        if self.record_factory is None:
            return record
        try:
            if isinstance(self.record_factory, type):
                return self.record_factory(**record)
            return self.record_factory(record)
        except (AttributeError, KeyError, TypeError, ValueError):
            self.logger.warning(
                "Infobox record_factory failed. Falling back to raw record: %s",
                record,
                exc_info=True,
            )
            return record

    def _handle_scrape_error(
        self,
        error: ScraperError,
        *,
        handler: ErrorHandler,
        cause: BaseException | None = None,
    ) -> dict[str, Any]:
        if handler.handle(error):
            return {}
        if cause is not None:
            raise error from cause
        raise error

    def _apply_transformers(self, record: dict[str, Any]) -> Any:
        return apply_transformers_with_factory(
            self.transformers,
            record,
            self.record_factory,
            self.logger,
        )

    # ------------------------------
    # Internal helpers
    # ------------------------------

    def _fetch(self, url: str) -> str:
        return self.fetcher.get_text(url, timeout=self.timeout)
