"""Template for creating a new single-article scraper module.

Usage (copy + rename + fill hooks):
1) copy this file to the target domain directory (e.g. ``scrapers/<domain>/...``),
2) rename classes/constants to the final domain names,
3) fill standard hooks from ``SingleWikiArticleScraperBase``:
   ``_build_infobox_payload``, ``_build_tables_payload``,
   ``_build_sections_payload``, ``_assemble_record``,
4) keep the ``SCRAPER_TEMPLATE_CONFIG`` contract unchanged for review consistency.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any
from typing import ClassVar

from bs4 import BeautifulSoup

from scrapers.base.single_wiki_article import InfoboxPayloadDTO
from scrapers.base.single_wiki_article import SectionsPayloadDTO
from scrapers.base.single_wiki_article import SingleWikiArticleScraperBase
from scrapers.base.single_wiki_article import TablesPayloadDTO


@dataclass(frozen=True, slots=True)
class SingleScraperTemplateConfig:
    """Uniform configuration contract for single scraper modules."""

    domain: str
    base_url: str


SCRAPER_TEMPLATE_CONFIG = SingleScraperTemplateConfig(
    domain="TODO_domain",
    base_url="https://en.wikipedia.org/wiki/TODO_article",
)


class TODOSingleScraper(SingleWikiArticleScraperBase):
    """TODO: replace with real single scraper docstring."""

    options_domain: ClassVar[str | None] = SCRAPER_TEMPLATE_CONFIG.domain
    options_profile: ClassVar[str] = "article_strict"

    def _build_infobox_payload(self, soup: BeautifulSoup) -> InfoboxPayloadDTO:
        _ = soup
        # TODO: parse + normalize infobox payload.
        return InfoboxPayloadDTO()

    def _build_tables_payload(self, soup: BeautifulSoup) -> TablesPayloadDTO:
        _ = soup
        # TODO: parse + normalize tables payload.
        return TablesPayloadDTO()

    def _build_sections_payload(self, soup: BeautifulSoup) -> SectionsPayloadDTO:
        _ = soup
        # TODO: parse + normalize sections payload.
        return SectionsPayloadDTO()

    def _assemble_record(
        self,
        *,
        soup: BeautifulSoup,
        infobox_payload: InfoboxPayloadDTO,
        tables_payload: TablesPayloadDTO,
        sections_payload: SectionsPayloadDTO,
    ) -> dict[str, Any]:
        _ = soup
        # TODO: return domain record assembled from payload DTOs.
        return {
            "url": self.url,
            "infobox": infobox_payload.data,
            "tables": tables_payload.data,
            "sections": sections_payload.data,
        }
