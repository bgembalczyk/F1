from abc import ABC
from abc import abstractmethod
import os
from typing import Literal

from infrastructure.gemini.client import GeminiClient
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
    def create_scraper_kwargs(self, _job: ListJobRegistryEntry) -> dict[str, object]:
        scraper_kwargs: dict[str, object] = {}
        raw_policy = os.getenv("GEMINI_ERROR_POLICY", "fallback").strip().lower()
        policy: Literal["retry", "fallback", "fail-fast"]
        if raw_policy in {"retry", "fallback", "fail-fast"}:
            policy = raw_policy
        else:
            policy = "fallback"
        try:
            gemini_client = GeminiClient.from_key_file()
            classifier = ParenClassifier(gemini_client=gemini_client).with_error_policy(
                policy=policy,
                retry_attempts=2,
            )
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
