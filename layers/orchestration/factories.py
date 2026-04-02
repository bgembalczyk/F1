from abc import ABC
from abc import abstractmethod

from infrastructure.gemini.client import GeminiClient
from layers.orchestration.protocols import LayerZeroRunConfigFactoryProtocol
from layers.seed.registry.entries import ListJobRegistryEntry
from scrapers.sponsorship_liveries.helpers.paren_classifier import ParenClassifier


class LayerZeroRunConfigFactory(LayerZeroRunConfigFactoryProtocol, ABC):
    @abstractmethod
    def create_scraper_kwargs(self, job: ListJobRegistryEntry) -> dict[str, object]:
        """Build scraper kwargs for layer-zero list job."""


class DefaultLayerZeroRunConfigFactory(LayerZeroRunConfigFactory):
    def create_scraper_kwargs(self, job: ListJobRegistryEntry) -> dict[str, object]:
        return {}


class StaticScraperKwargsFactory(LayerZeroRunConfigFactory):
    def __init__(self, *, scraper_kwargs: dict[str, object]) -> None:
        self._scraper_kwargs = dict(scraper_kwargs)

    def create_scraper_kwargs(self, job: ListJobRegistryEntry) -> dict[str, object]:
        return dict(self._scraper_kwargs)


class SponsorshipLiveriesRunConfigFactory(LayerZeroRunConfigFactory):
    def create_scraper_kwargs(self, job: ListJobRegistryEntry) -> dict[str, object]:
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
