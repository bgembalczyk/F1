from typing import Any, Dict
from bs4 import BeautifulSoup

import logging

from scrapers.base.error_handler import ErrorHandler
from scrapers.base.errors import ScraperError
from scrapers.base.html_fetcher import HtmlFetcher
from scrapers.base.infobox.helpers import parse_infobox_from_soup
from scrapers.base.options import ScraperOptions
from scrapers.base.infobox.field_mapper import InfoboxFieldMapper
from scrapers.base.infobox.html_parser import InfoboxHtmlParser
from scrapers.base.logging import get_logger
from scrapers.base.transformers import RecordFactoryTransformer, TransformersPipeline


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
        self.transformers = list(options.transformers or [])

    # ------------------------------
    # Public API
    # ------------------------------

    def scrape(self, url: str) -> Dict[str, Any]:
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
        except Exception as exc:
            error = (
                exc
                if isinstance(exc, ScraperError)
                else handler.wrap_network(exc, url=url)
            )
            if handler.handle(error):
                return {}
            if error is exc:
                raise
            raise error from exc

        try:
            soup = BeautifulSoup(html, "html.parser")
            raw = parse_infobox_from_soup(self, soup)
            return self._apply_transformers(raw)
        except Exception as exc:
            error = (
                exc
                if isinstance(exc, ScraperError)
                else handler.wrap_parse(exc, url=url)
            )
            if handler.handle(error):
                return {}
            if error is exc:
                raise
            raise error from exc

    def apply_record_factory(self, record: Dict[str, Any]) -> Any:
        if self.record_factory is None:
            return record
        try:
            if isinstance(self.record_factory, type):
                return self.record_factory(**record)
            return self.record_factory(record)
        except Exception:
            self.logger.warning(
                "Infobox record_factory failed. Falling back to raw record: %s",
                record,
                exc_info=True,
            )
            return record

    def _apply_transformers(self, record: Dict[str, Any]) -> Any:
        transformers = list(self.transformers)
        if self.record_factory is not None:
            transformers.append(
                RecordFactoryTransformer(
                    self.record_factory,
                    fallback_on_error=True,
                )
            )
        if not transformers:
            return record
        pipeline = TransformersPipeline(transformers, logger=self.logger)
        transformed = pipeline.apply([record])
        return transformed[0] if transformed else {}

    # ------------------------------
    # Internal helpers
    # ------------------------------

    def _fetch(self, url: str) -> str:
        return self.fetcher.get_text(url, timeout=self.timeout)
