from abc import ABC
from typing import TYPE_CHECKING
from typing import Any

from bs4 import BeautifulSoup

from scrapers.base.abc import AbstractScraper
from scrapers.base.helpers.helpers import init_scraper_options
from scrapers.base.options import ScraperOptions
from scrapers.wiki.parsers.body_content import BodyContentParser
from scrapers.wiki.parsers.elements.parsers import WikiElementParsers
from scrapers.wiki.parsers.elements.parsers import build_default_wiki_element_parsers
from scrapers.wiki.parsers.header import HeaderParser
from scrapers.wiki.parsers.sections.sub_sub_sub_section import WikiElementParserMixin

if TYPE_CHECKING:
    from scrapers.wiki.parsers.sections.section import SectionParser


class AbstractWikiScraper(WikiElementParserMixin, AbstractScraper, ABC):
    """Base template for Wikipedia-source scrapers."""

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
        resolved_element_parsers = (
            element_parsers or build_default_wiki_element_parsers()
        )
        options = init_scraper_options(options)
        super().__init__(
            options=options,
            element_parsers=resolved_element_parsers,
        )
        self.header_parser = header_parser or HeaderParser()
        self.body_content_parser = body_content_parser or BodyContentParser(
            element_parsers=resolved_element_parsers,
        )
        self.section_parser: SectionParser = (
            self.body_content_parser.content_text_parser.section_parser
        )

    def build_parser(self) -> tuple[HeaderParser, BodyContentParser]:
        return self.header_parser, self.body_content_parser

    def build_record(self, soup: BeautifulSoup) -> dict[str, Any]:
        header_parser, body_parser = self.build_parser()
        result: dict[str, Any] = {
            "url": self.url,
            "header": None,
            "body_content": None,
        }

        header_el = HeaderParser.find_header(soup)
        if header_el is not None:
            result["header"] = header_parser.parse(header_el)

        body_content_el = BodyContentParser.find_body_content(soup)
        if body_content_el is not None:
            result["body_content"] = body_parser.parse(body_content_el)
        return result

    def parse_records(self, soup: BeautifulSoup) -> list[dict[str, Any]]:
        return [self.build_record(soup)]

    def scrape(self, url: str) -> dict[str, Any]:
        self.url = url
        records = self.fetch()
        return records[0] if records else {}


class WikiScraper(AbstractWikiScraper):
    """Concrete wiki scraper entry class."""


__all__ = ["AbstractWikiScraper", "WikiScraper"]
