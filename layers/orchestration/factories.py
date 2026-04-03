from abc import ABC
from abc import abstractmethod

from layers.orchestration.protocols import LayerZeroRunConfigFactoryProtocol
from layers.orchestration.protocols import SponsorshipClassifierBuilder
from layers.seed.registry.entries import ListJobRegistryEntry
from scrapers.base.logging import build_execution_context
from scrapers.base.logging import get_logger


class LayerZeroRunConfigFactory(LayerZeroRunConfigFactoryProtocol, ABC):
    @abstractmethod
    def create_scraper_kwargs(self, _job: ListJobRegistryEntry) -> dict[str, object]:
        """Build scraper kwargs for layer-zero list job."""


class DefaultLayerZeroRunConfigFactory(LayerZeroRunConfigFactory):
    def create_scraper_kwargs(self, job: ListJobRegistryEntry) -> dict[str, object]:
        _ = job
        return {}


class StaticScraperKwargsFactory(LayerZeroRunConfigFactory):
    def __init__(self, *, scraper_kwargs: dict[str, object]) -> None:
        self._scraper_kwargs = dict(scraper_kwargs)

    def create_scraper_kwargs(self, job: ListJobRegistryEntry) -> dict[str, object]:
        _ = job
        return dict(self._scraper_kwargs)


class SponsorshipLiveriesRunConfigFactory(LayerZeroRunConfigFactory):
    def __init__(
        self,
        *,
        classifier_builder: SponsorshipClassifierBuilder | None = None,
    ) -> None:
        self._classifier_builder = classifier_builder
        self._logger = get_logger(self.__class__.__name__)

    def create_scraper_kwargs(self, job: ListJobRegistryEntry) -> dict[str, object]:
        context = build_execution_context(
            seed_name=job.seed_name,
            domain=job.output_category,
            source_name=job.list_scraper_cls.__name__,
        )
        scraper_kwargs: dict[str, object] = {}
        try:
            if self._classifier_builder is None:
                return scraper_kwargs

            scraper_kwargs["classifier"] = self._classifier_builder()
            self._logger.info(
                "Gemini ParenClassifier loaded; annotations classification enabled",
                extra=context,
            )
        except FileNotFoundError as e:
            self._logger.warning(
                "Gemini API key missing; Gemini classification disabled (%s)",
                e,
                extra=context,
            )
        return scraper_kwargs
