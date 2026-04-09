from infrastructure.gemini.client import GeminiClient
from layers.seed.registry.entries import ListJobRegistryEntry
from layers.zero.run_config_factories.base import LayerZeroRunConfigFactory
from scrapers.base.logging import build_execution_context
from scrapers.base.logging import get_logger
from scrapers.sponsorship_liveries.helpers.paren_classifier import ParenClassifier


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
