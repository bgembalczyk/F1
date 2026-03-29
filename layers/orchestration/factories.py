from abc import ABC
from abc import abstractmethod

from infrastructure.gemini.client import GeminiClient
from layers.orchestration.progress_reporter import ProgressReporter
from layers.seed.registry.entries import ListJobRegistryEntry
from scrapers.sponsorship_liveries.helpers.paren_classifier import ParenClassifier


class LayerZeroRunConfigFactory(ABC):
    @abstractmethod
    def create_scraper_kwargs(self, _job: ListJobRegistryEntry) -> dict[str, object]:
        """Build scraper kwargs for layer-zero list job."""


class DefaultLayerZeroRunConfigFactory(LayerZeroRunConfigFactory):
    def create_scraper_kwargs(self, _job: ListJobRegistryEntry) -> dict[str, object]:
        return {}


class SponsorshipLiveriesRunConfigFactory(LayerZeroRunConfigFactory):
    def __init__(self, *, progress_reporter: ProgressReporter) -> None:
        self._progress_reporter = progress_reporter

    def create_scraper_kwargs(self, _job: ListJobRegistryEntry) -> dict[str, object]:
        scraper_kwargs: dict[str, object] = {}
        try:
            gemini_client = GeminiClient.from_key_file()
            classifier = ParenClassifier(gemini_client=gemini_client)
            scraper_kwargs["classifier"] = classifier
            self._progress_reporter.warn(
                "main",
                "Gemini ParenClassifier",
                "załadowany - adnotacje w nawiasach będą klasyfikowane.",
            )
        except FileNotFoundError as e:
            self._progress_reporter.warn(
                "main",
                "Gemini ParenClassifier",
                f"Brak klucza Gemini API ({e}), klasyfikacja Gemini wyłączona.",
            )
        return scraper_kwargs
