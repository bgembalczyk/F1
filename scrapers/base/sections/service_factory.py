from __future__ import annotations

from typing import TYPE_CHECKING
from typing import Protocol
from typing import TypeVar

if TYPE_CHECKING:
    from scrapers.base.options import ScraperOptions
    from scrapers.base.sections.adapter import SectionAdapter

SectionServiceT = TypeVar("SectionServiceT")


class SectionServiceFactory(Protocol[SectionServiceT]):
    def create(
        self,
        *,
        adapter: SectionAdapter,
        options: ScraperOptions,
        url: str,
    ) -> SectionServiceT: ...
