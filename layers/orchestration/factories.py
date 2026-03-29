from abc import ABC
from abc import abstractmethod
from typing import Protocol

from infrastructure.gemini.client import GeminiClient
from layers.seed.registry.entries import ListJobRegistryEntry
from scrapers.sponsorship_liveries.helpers.paren_classifier import ParenClassifier


class LayerZeroRunConfigFactoryProtocol(Protocol):
    def create_scraper_kwargs(self, job: ListJobRegistryEntry) -> dict[str, object]:
        """Build scraper kwargs for layer-zero list job."""


class LayerZeroRunConfigFactory(ABC):
    @abstractmethod
    def create_scraper_kwargs(self, _job: ListJobRegistryEntry) -> dict[str, object]:
        """Build scraper kwargs for layer-zero list job."""


class DefaultLayerZeroRunConfigFactory(LayerZeroRunConfigFactory):
    def create_scraper_kwargs(self, _job: ListJobRegistryEntry) -> dict[str, object]:
        return {}


class SponsorshipLiveriesRunConfigFactory(LayerZeroRunConfigFactory):
    def create_scraper_kwargs(self, _job: ListJobRegistryEntry) -> dict[str, object]:
        scraper_kwargs: dict[str, object] = {}
        try:
            gemini_client = GeminiClient.from_key_file()
            classifier = ParenClassifier(gemini_client=gemini_client)
            scraper_kwargs["classifier"] = classifier
            print(
                "[main] Gemini ParenClassifier załadowany - "
                "adnotacje w nawiasach będą klasyfikowane.",
            )
        except FileNotFoundError as e:
            print(
                "[main] Brak klucza Gemini API "
                f"({e}), klasyfikacja Gemini wyłączona.",
            )
        return scraper_kwargs
