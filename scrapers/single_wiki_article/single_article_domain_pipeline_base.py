from __future__ import annotations

from abc import ABC
from abc import abstractmethod
from typing import TYPE_CHECKING
from typing import Any
from typing import ClassVar

from scrapers.dto import InfoboxPayloadDTO
from scrapers.dto import SectionsPayloadDTO
from scrapers.dto import TablesPayloadDTO
from scrapers.single_wiki_article.single_article_scraper_base import (
    SingleArticleScraperBase,
)
from scrapers.single_wiki_article.single_article_section_aware_mixin import (
    SingleArticleSectionAwareMixin,
)

if TYPE_CHECKING:
    from bs4 import BeautifulSoup


class SingleArticleDomainPipelineBase(
    SingleArticleSectionAwareMixin,
    SingleArticleScraperBase,
    ABC,
):
    """Pośrednia baza z hookami domenowymi pipeline rekordu."""

    STANDARD_HOOKS: ClassVar[dict[str, str]] = {
        "_build_infobox_payload": "Build normalized infobox payload.",
        "_build_tables_payload": "Build normalized table payload.",
        "_build_sections_payload": "Build normalized section payload.",
        "_assemble_record": "Compose final domain record from payload hooks.",
    }

    def _build_article_record(self, soup: BeautifulSoup) -> dict[str, Any]:
        return self._run_record_pipeline(soup)

    def _run_record_pipeline(self, soup: BeautifulSoup) -> dict[str, Any]:
        self._before_payload_build(soup)
        record = self._assemble_record(
            soup=soup,
            infobox_payload=self._build_infobox_payload(soup),
            tables_payload=self._build_tables_payload(soup),
            sections_payload=self._build_sections_payload(soup),
        )
        return self._after_record_assembled(record, soup)

    def _before_payload_build(self, soup: BeautifulSoup) -> None:
        _ = soup

    def _after_record_assembled(
        self,
        record: dict[str, Any],
        soup: BeautifulSoup,
    ) -> dict[str, Any]:
        _ = soup
        return record

    def _build_infobox_payload(self, soup: BeautifulSoup) -> InfoboxPayloadDTO:
        _ = soup
        return InfoboxPayloadDTO()

    def _build_tables_payload(self, soup: BeautifulSoup) -> TablesPayloadDTO:
        _ = soup
        return TablesPayloadDTO()

    def _build_sections_payload(self, soup: BeautifulSoup) -> SectionsPayloadDTO:
        _ = soup
        return SectionsPayloadDTO()

    @abstractmethod
    def _assemble_record(
        self,
        *,
        soup: BeautifulSoup,
        infobox_payload: InfoboxPayloadDTO,
        tables_payload: TablesPayloadDTO,
        sections_payload: SectionsPayloadDTO,
    ) -> dict[str, Any]:
        """Compose final domain record from template-method payload hooks."""


__all__ = ["SingleArticleDomainPipelineBase"]
