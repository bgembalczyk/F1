from __future__ import annotations

from abc import ABC
from abc import abstractmethod
from collections.abc import Callable
from pathlib import Path

from infrastructure.gemini.client import GeminiClient
from scrapers.base.helpers.runner import run_and_export
from scrapers.base.run_config import RunConfig
from scrapers.circuits.helpers.export import export_complete_circuits
from scrapers.constructors.helpers.export import export_complete_constructors
from scrapers.drivers.helpers.export import export_complete_drivers
from scrapers.engines.helpers.export import export_complete_engine_manufacturers
from scrapers.grands_prix.complete_scraper import F1CompleteGrandPrixDataExtractor
from scrapers.seasons.helpers import export_complete_seasons
from scrapers.sponsorship_liveries.helpers.paren_classifier import ParenClassifier
from scrapers.wiki.seed_registry import ListJobRegistryEntry
from scrapers.wiki.seed_registry import SeedRegistryEntry

LayerOneExportFn = Callable[..., None]


class LayerJobRunner(ABC):
    @abstractmethod
    def run(self, seed: SeedRegistryEntry, run_config: RunConfig, base_wiki_dir: Path) -> None:
        """Execute layer-one job for given seed."""


class FunctionLayerJobRunner(LayerJobRunner):
    def __init__(self, export_fn: LayerOneExportFn) -> None:
        self._export_fn = export_fn

    def run(self, seed: SeedRegistryEntry, run_config: RunConfig, base_wiki_dir: Path) -> None:
        self._export_fn(
            output_dir=base_wiki_dir / seed.default_output_path,
            include_urls=run_config.include_urls,
        )


class RunAndExportLayerJobRunner(LayerJobRunner):
    def __init__(self, extractor_cls: type[object]) -> None:
        self._extractor_cls = extractor_cls

    def run(self, seed: SeedRegistryEntry, run_config: RunConfig, base_wiki_dir: Path) -> None:
        run_and_export(
            self._extractor_cls,
            seed.default_output_path,
            run_config=run_config,
        )


LAYER_ONE_STRATEGIES: dict[str, LayerJobRunner] = {
    "circuits": FunctionLayerJobRunner(export_complete_circuits),
    "drivers": FunctionLayerJobRunner(export_complete_drivers),
    "seasons": FunctionLayerJobRunner(export_complete_seasons),
    "constructors": FunctionLayerJobRunner(export_complete_constructors),
    "grands_prix": RunAndExportLayerJobRunner(F1CompleteGrandPrixDataExtractor),
}


class LayerZeroRunConfigFactory(ABC):
    @abstractmethod
    def create_scraper_kwargs(self, job: ListJobRegistryEntry) -> dict[str, object]:
        """Build scraper kwargs for layer-zero list job."""


class DefaultLayerZeroRunConfigFactory(LayerZeroRunConfigFactory):
    def create_scraper_kwargs(self, job: ListJobRegistryEntry) -> dict[str, object]:
        return {}


class SponsorshipLiveriesRunConfigFactory(LayerZeroRunConfigFactory):
    def create_scraper_kwargs(self, job: ListJobRegistryEntry) -> dict[str, object]:
        scraper_kwargs: dict[str, object] = {}
        try:
            gemini_client = GeminiClient.from_key_file()
            classifier = ParenClassifier(gemini_client)
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


def build_layer_one_runner_map() -> dict[str, LayerJobRunner]:
    return {seed_name: runner for seed_name, runner in LAYER_ONE_STRATEGIES.items()}


def build_layer_zero_run_config_factory_map() -> dict[str, LayerZeroRunConfigFactory]:
    return {
        "sponsorship_liveries": SponsorshipLiveriesRunConfigFactory(),
    }


def run_engine_manufacturers(base_wiki_dir: Path, include_urls: bool) -> None:
    print("[complete] running  F1CompleteEngineManufacturerDataExtractor")
    export_complete_engine_manufacturers(
        output_dir=base_wiki_dir / "engines/complete_engine_manufacturers",
        include_urls=include_urls,
    )
    print("[complete] finished F1CompleteEngineManufacturerDataExtractor")
