from abc import ABC
from abc import abstractmethod
from typing import Any

from bs4 import BeautifulSoup

from scrapers.base.sections.adapter import SectionAdapter
from scrapers.base.single_wiki_article.base import SingleWikiArticleScraperBase


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

