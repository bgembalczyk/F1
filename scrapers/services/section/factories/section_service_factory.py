from __future__ import annotations

from abc import ABC
from abc import abstractmethod
from typing import Generic
from typing import TypeVar

from models.wiki_url import WikiUrl
from scrapers.options import ScraperOptions

from scrapers.single_wiki_article.single_article_scraper_base import ArticleScraperBase

ServiceT_co = TypeVar("ServiceT_co", covariant=True)


class SectionServiceFactoryABC(ABC, Generic[ServiceT_co]):
    """Factory contract for building section services in single-article scrapers."""

    @abstractmethod
    def create(
        self,
        *,
        adapter: ArticleScraperBase,
        options: ScraperOptions | None = None,
        url: WikiUrl | str | None = None,
    ) -> ServiceT_co: ...


__all__ = ["SectionServiceFactoryABC"]
