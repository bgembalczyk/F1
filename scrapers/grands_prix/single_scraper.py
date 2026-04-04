from __future__ import annotations

from typing import TYPE_CHECKING
from typing import Any

from scrapers.base.errors import ScraperError
from scrapers.base.sections.constants import DOMAIN_SECTION_RESOLVER_CONFIG
from scrapers.base.sections.section_id_resolver import MissingSectionError
from scrapers.base.sections.section_id_resolver import SectionIdResolver
from scrapers.base.single_wiki_article.dto import InfoboxPayloadDTO
from scrapers.base.single_wiki_article.dto import SectionsPayloadDTO
from scrapers.base.single_wiki_article.dto import TablesPayloadDTO
from scrapers.base.single_wiki_article.base import SingleWikiArticleScraperBase
from scrapers.base.single_wiki_article.section_selection_strategy import (
    WikipediaSectionByIdSelectionStrategy,
)
from scrapers.grands_prix.helpers.sections import is_grand_prix_article
from scrapers.grands_prix.sections.by_year import GrandPrixByYearSectionParser

if TYPE_CHECKING:
    from bs4 import BeautifulSoup

    from scrapers.base.options import ScraperOptions


class F1SingleGrandPrixScraper(SingleWikiArticleScraperBase):
    def __init__(self, *, options: ScraperOptions | None = None) -> None:
        super().__init__(
            options=options,
            section_selection_strategy=WikipediaSectionByIdSelectionStrategy(
                domain="grands_prix",
            ),
        )

    def _try_parse_section(
        self,
        soup: BeautifulSoup,
        section_id: str,
    ) -> list[dict[str, Any]] | None:
        section_fragment = self.extract_section_by_id(
            soup,
            section_id,
            domain="grands_prix",
        )
        if section_fragment is None:
            missing_error = MissingSectionError(
                domain="grands_prix",
                section_id=section_id,
                candidates=(section_id,),
            ).as_domain_error(url=self.url)
            if self._handle_scraper_error(missing_error):
                return None
            raise missing_error

        try:
            parser = GrandPrixByYearSectionParser(
                url=self.url,
                include_urls=self.include_urls,
                normalize_empty_values=self.normalize_empty_values,
            )
            result = parser.parse(section_fragment)
            section_records = result.records
        except Exception as exc:
            error: Exception = (
                exc if isinstance(exc, ScraperError) else self._wrap_parse_error(exc)
            )
            if self._handle_scraper_error(error):
                return None
            if error is exc:
                raise
            raise error from exc
        return [
            {
                "url": self.url,
                "by_year": section_records,
                "section_id": section_id,
            },
        ]

    def parse(self, soup: BeautifulSoup) -> list[dict[str, Any]]:
        if not is_grand_prix_article(soup):
            return []

        by_year = DOMAIN_SECTION_RESOLVER_CONFIG["grands_prix"][0]
        resolver = SectionIdResolver(domain="grands_prix")
        for section_id in resolver.resolve_candidates(
            section_id=by_year.section_id,
            alternative_section_ids=by_year.alternative_section_ids,
        ):
            result = self._try_parse_section(soup, section_id)
            if result is not None:
                return result
        return [{"url": self.url, "by_year": []}]

    def _assemble_record(
        self,
        *,
        soup: BeautifulSoup,
        infobox_payload: InfoboxPayloadDTO,
        tables_payload: TablesPayloadDTO,
        sections_payload: SectionsPayloadDTO,
    ) -> dict[str, Any]:
        _ = infobox_payload
        _ = tables_payload
        _ = sections_payload
        parsed = self.parse(soup)
        return parsed[0] if parsed else {"url": self.url, "by_year": []}
