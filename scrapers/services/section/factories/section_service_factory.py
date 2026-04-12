from __future__ import annotations

from abc import ABC
from abc import abstractmethod
from typing import Generic
from typing import TypeVar

from models.wiki_url import WikiUrl
from scrapers.adapters.section.adapter import SectionAdapter
from scrapers.options import ScraperOptions

ServiceT_co = TypeVar("ServiceT_co", covariant=True)


class SectionServiceFactoryABC(ABC, Generic[ServiceT_co]):
    """Factory contract for building section services in single-article scrapers."""

    @abstractmethod
    def create(
        self,
        *,
        adapter: SectionAdapter,
        options: ScraperOptions | None = None,
        url: WikiUrl | str | None = None,
    ) -> ServiceT_co: ...


# Backward-compatible alias for previous name.
SectionServiceFactory = SectionServiceFactoryABC

__all__ = ["SectionServiceFactoryABC", "SectionServiceFactory"]
