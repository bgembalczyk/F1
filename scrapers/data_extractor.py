from __future__ import annotations

from abc import abstractmethod
from typing import Any

from scrapers.base.options import ScraperOptions
from scrapers.runtime.base_runtime_component import BaseRuntimeComponent


class BaseCompositeExtractor(BaseRuntimeComponent):
    """Bazowa klasa dla ekstraktorów orkiestrujących wiele scraperów."""

    @abstractmethod
    def fetch(self) -> list[Any]:
        """Pobierz i zwróć listę rekordów (może być pusta)."""


class BaseDataExtractor(BaseCompositeExtractor):
    """Thin compatibility alias: use BaseCompositeExtractor as canonical base."""

    def __init__(self, *, options: ScraperOptions) -> None:
        super().__init__(options=options)
