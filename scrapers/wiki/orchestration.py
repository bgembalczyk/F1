from __future__ import annotations

from abc import ABC
from abc import abstractmethod
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
from scrapers.wiki.discovery import build_layer_one_runner_map_discovered
from scrapers.wiki.seed_registry import ListJobRegistryEntry
from scrapers.wiki.seed_registry import SeedRegistryEntry


class LayerJobRunner(ABC):
    @abstractmethod
    def run(
        self,
        seed: SeedRegistryEntry,
        run_config: RunConfig,
        base_wiki_dir: Path,
    ) -> None:
        """Execute layer-one job for given seed."""


class GrandPrixRunner(LayerJobRunner):
    COMPONENT_METADATA = {
        "domain": "grands_prix",
        "seed_name": "grands_prix",
        "layer": "layer_one",
        "output_category": "grands_prix",
        "component_type": "runner",
    }

    def run(
        self,
        seed: SeedRegistryEntry,
        run_config: RunConfig,
        base_wiki_dir: Path,
    ) -> None:
        run_and_export(
            F1CompleteGrandPrixDataExtractor,
            seed.default_output_path,
            run_config=run_config,
        )


class CircuitsRunner(LayerJobRunner):
    COMPONENT_METADATA = {
        "domain": "circuits",
        "seed_name": "circuits",
        "layer": "layer_one",
        "output_category": "circuits",
        "component_type": "runner",
    }

    def run(
        self,
        seed: SeedRegistryEntry,
        run_config: RunConfig,
        base_wiki_dir: Path,
    ) -> None:
        export_complete_circuits(
            output_dir=base_wiki_dir / seed.default_output_path,
            include_urls=run_config.include_urls,
        )


class DriversRunner(LayerJobRunner):
    COMPONENT_METADATA = {
        "domain": "drivers",
        "seed_name": "drivers",
        "layer": "layer_one",
        "output_category": "drivers",
        "component_type": "runner",
    }

    def run(
        self,
        seed: SeedRegistryEntry,
        run_config: RunConfig,
        base_wiki_dir: Path,
    ) -> None:
        export_complete_drivers(
            output_dir=base_wiki_dir / seed.default_output_path,
            include_urls=run_config.include_urls,
        )


class SeasonsRunner(LayerJobRunner):
    COMPONENT_METADATA = {
        "domain": "seasons",
        "seed_name": "seasons",
        "layer": "layer_one",
        "output_category": "seasons",
        "component_type": "runner",
    }

    def run(
        self,
        seed: SeedRegistryEntry,
        run_config: RunConfig,
        base_wiki_dir: Path,
    ) -> None:
        export_complete_seasons(
            output_dir=base_wiki_dir / seed.default_output_path,
            include_urls=run_config.include_urls,
        )


class ConstructorsRunner(LayerJobRunner):
    COMPONENT_METADATA = {
        "domain": "constructors",
        "seed_name": "constructors",
        "layer": "layer_one",
        "output_category": "constructors",
        "component_type": "runner",
    }

    def run(
        self,
        seed: SeedRegistryEntry,
        run_config: RunConfig,
        base_wiki_dir: Path,
    ) -> None:
        export_complete_constructors(
            output_dir=base_wiki_dir / seed.default_output_path,
            include_urls=run_config.include_urls,
        )


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
    explicit_runner_map: dict[str, LayerJobRunner] = {
        "grands_prix": GrandPrixRunner(),
        "circuits": CircuitsRunner(),
        "drivers": DriversRunner(),
        "seasons": SeasonsRunner(),
        "constructors": ConstructorsRunner(),
    }
    discovered_runner_map = build_layer_one_runner_map_discovered()
    merged = dict(discovered_runner_map)
    for seed_name, runner in explicit_runner_map.items():
        merged.setdefault(seed_name, runner)
    return merged


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
