from __future__ import annotations

from abc import ABC
from abc import abstractmethod
from typing import TYPE_CHECKING

from infrastructure.gemini.client import GeminiClient
from layers.zero.run_config_factories.protocol import LayerZeroRunConfigFactoryProtocol
from scrapers.base.logging import build_execution_context
from scrapers.base.logging import get_logger
from scrapers.sponsorship_liveries.helpers.paren_classifier import ParenClassifier

if TYPE_CHECKING:
    from layers.seed.registry.entries import ListJobRegistryEntry


class LayerZeroRunConfigFactory(LayerZeroRunConfigFactoryProtocol, ABC):
    @abstractmethod
    def create_scraper_kwargs(
        self,
        job: ListJobRegistryEntry | None = None,
    ) -> dict[str, object]:
        """Build scraper kwargs for layer-zero list job."""






