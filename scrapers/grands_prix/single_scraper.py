from __future__ import annotations

from typing import TYPE_CHECKING
from typing import Any

from scrapers.base.errors import DomainParseError
from scrapers.base.errors import ScraperError
from scrapers.base.sections.constants import DOMAIN_CRITICAL_SECTIONS
from scrapers.base.sections.resolve_candidates import resolve_section_candidates
from scrapers.base.single_wiki_article import SingleWikiArticleScraperBase
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

    def _missing_section_error(
        self,
        *,
        section_id: str,
        cause: RuntimeError,
    ) -> DomainParseError:
        msg = f"Brak sekcji {section_id!r} w artykule."
        return DomainParseError(msg, url=self.url, cause=cause)

    @staticmethod
    def _raise_missing_section_error(section_id: str) -> None:
        msg = f"Missing section: {section_id}"
        raise RuntimeError(msg)

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
                self._raise_missing_section_error(section_id)
            else:
                parser = GrandPrixByYearSectionParser(
                    url=self.url,
                    include_urls=self.include_urls,
                    normalize_empty_values=self.normalize_empty_values,
                )
                result = parser.parse(section_fragment)
                section_records = result.records
                return [
                    {
                        "url": self.url,
                        "by_year": section_records,
                        "section_id": section_id,
                    },
                ]
        except Exception as exc:
            if isinstance(exc, RuntimeError):
                error: Exception = self._missing_section_error(
                    section_id=section_id,
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
