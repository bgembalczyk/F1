from __future__ import annotations

from typing import TYPE_CHECKING
from typing import Any

from scrapers.base.errors import DomainParseError
from scrapers.base.errors import ScraperError
from scrapers.base.options import ScraperOptions
from scrapers.base.sections.critical_sections import DOMAIN_CRITICAL_SECTIONS
from scrapers.base.sections.critical_sections import resolve_section_candidates
from scrapers.base.single_wiki_article import SingleWikiArticleSectionByIdBase
from scrapers.grands_prix.helpers.article_validation import is_grand_prix_article
from scrapers.grands_prix.postprocess import GrandPrixSectionContractPostProcessor
from scrapers.grands_prix.sections.by_year import GrandPrixByYearSectionParser

if TYPE_CHECKING:
    from bs4 import BeautifulSoup


class F1SingleGrandPrixScraper(SingleWikiArticleSectionByIdBase):
    def __init__(self, *, options: ScraperOptions | None = None) -> None:
        super().__init__(options=options)

    def _build_post_processor(self) -> GrandPrixSectionContractPostProcessor:
        return GrandPrixSectionContractPostProcessor()

    def _try_parse_section(
        self,
        soup: BeautifulSoup,
        section_id: str,
    ) -> list[dict[str, Any]] | None:
        try:
            section_fragment = self.extract_section_by_id(
                soup,
                section_id,
                domain="grands_prix",
            )
            if section_fragment is None:
                raise RuntimeError(f"Missing section: {section_id}")
            parser = GrandPrixByYearSectionParser(
                url=self.url,
                include_urls=self.include_urls,
                normalize_empty_values=self.normalize_empty_values,
            )
            result = parser.parse(section_fragment)
            return [
                {"url": self.url, "by_year": result.records, "section_id": section_id},
            ]
        except Exception as exc:
            if isinstance(exc, RuntimeError):
                error: Exception = DomainParseError(
                    f"Brak sekcji {section_id!r} w artykule.",
                    url=self.url,
                    cause=exc,
                )
            else:
                error = (
                    exc
                    if isinstance(exc, ScraperError)
                    else self._wrap_parse_error(exc)
                )
            if self._handle_scraper_error(error):
                return None
            if error is exc:
                raise
            raise error from exc

    def parse(self, soup: BeautifulSoup) -> list[dict[str, Any]]:
        if not is_grand_prix_article(soup):
            return []

        by_year = DOMAIN_CRITICAL_SECTIONS["grands_prix"][0]
        for section_id in resolve_section_candidates(
            domain="grands_prix",
            section_id=by_year.section_id,
            alternative_section_ids=by_year.alternative_section_ids,
        ):
            result = self._try_parse_section(soup, section_id)
            if result is not None:
                return result
        return [{"url": self.url, "by_year": []}]
