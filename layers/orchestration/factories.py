from __future__ import annotations

from abc import ABC
from abc import abstractmethod
from typing import TYPE_CHECKING

from layers.orchestration.protocols import LayerZeroRunConfigFactoryProtocol
from scrapers.base.logging import build_execution_context
from scrapers.base.logging import get_logger

if TYPE_CHECKING:
    from layers.seed.registry.entries import ListJobRegistryEntry


class LayerZeroRunConfigFactory(LayerZeroRunConfigFactoryProtocol, ABC):
    @abstractmethod
    def create_scraper_kwargs(
        self,
        job: ListJobRegistryEntry | None = None,
    ) -> dict[str, object]:
        """Build scraper kwargs for layer-zero list job."""


class DefaultLayerZeroRunConfigFactory(LayerZeroRunConfigFactory):
    def create_scraper_kwargs(
        self,
        job: ListJobRegistryEntry | None = None,
    ) -> dict[str, object]:
        _ = job
        return {}


class StaticScraperKwargsFactory(LayerZeroRunConfigFactory):
    def __init__(self, *, scraper_kwargs: dict[str, object]) -> None:
        self._scraper_kwargs = dict(scraper_kwargs)

    def create_scraper_kwargs(
        self,
        job: ListJobRegistryEntry | None = None,
    ) -> dict[str, object]:
        _ = job
        return dict(self._scraper_kwargs)


class SponsorshipLiveriesRunConfigFactory(LayerZeroRunConfigFactory):
    def __init__(self) -> None:
        self._logger = get_logger(self.__class__.__name__)

    def create_scraper_kwargs(self, job: ListJobRegistryEntry) -> dict[str, object]:
        context = build_execution_context(
            seed_name=job.seed_name,
            domain=job.output_category,
            source_name=job.list_scraper_cls.__name__,
        )
        scraper_kwargs: dict[str, object] = {}
        try:
            # Import lazily to avoid module-level circular imports during bootstrap.
            from infrastructure.gemini.client import GeminiClient
            from scrapers.sponsorship_liveries.helpers.paren_classifier import (
                ParenClassifier,
            )

            gemini_client = GeminiClient.from_key_file()
            classifier = ParenClassifier(gemini_client=gemini_client)
            scraper_kwargs["classifier"] = classifier
            self._logger.info(
                "Gemini ParenClassifier loaded; parentheses annotations "
                "classification enabled",
                extra=context,
            )
        except FileNotFoundError as e:
            self._logger.warning(
                "Gemini API key missing; Gemini classification disabled (%s)",
                e,
                extra=context,
            )
        return scraper_kwargs
