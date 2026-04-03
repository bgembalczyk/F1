from abc import ABC
from abc import abstractmethod

from infrastructure.gemini.client import GeminiClient
from layers.orchestration.protocols import LayerZeroRunConfigFactoryProtocol
from layers.seed.registry import ListJobRegistryEntry
from scrapers.base.logging import build_execution_context
from scrapers.base.logging import get_logger
from scrapers.sponsorship_liveries.helpers.paren_classifier import ParenClassifier


class LayerZeroRunConfigFactory(LayerZeroRunConfigFactoryProtocol, ABC):
    @abstractmethod
    def create_scraper_kwargs(self, job: ListJobRegistryEntry) -> dict[str, object]:
        """Build scraper kwargs for layer-zero list job."""


class DefaultLayerZeroRunConfigFactory(LayerZeroRunConfigFactory):
    def create_scraper_kwargs(self, _job: ListJobRegistryEntry) -> dict[str, object]:
        return {}


class StaticScraperKwargsFactory(LayerZeroRunConfigFactory):
    def __init__(self, *, scraper_kwargs: dict[str, object]) -> None:
        self._scraper_kwargs = dict(scraper_kwargs)

    def create_scraper_kwargs(self, _job: ListJobRegistryEntry) -> dict[str, object]:
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
            gemini_client = GeminiClient.from_key_file()
            classifier = ParenClassifier(gemini_client=gemini_client)
            scraper_kwargs["classifier"] = classifier
            self._logger.info(
                "Gemini ParenClassifier loaded; parentheses annotations classification enabled",
                extra=context,
            )
        except FileNotFoundError as e:
            self._logger.warning(
                "Gemini API key missing; Gemini classification disabled (%s)",
                e,
                extra=context,
            )
        return scraper_kwargs
