from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from uuid import uuid4

from layers.orchestration.protocols import LayerOneRunnerProtocol
from layers.seed.registry.entries import SeedRegistryEntry
from scrapers.base.logging import build_execution_context
from scrapers.base.logging import get_logger
from scrapers.base.run_config import RunConfig


@dataclass(frozen=True, slots=True)
class LayerOneExecutorDependencies:
    validate_seed_registry_function: Callable[
        [tuple[SeedRegistryEntry, ...]],
        None,
    ]
    runner_map_builder: Callable[[], dict[str, LayerOneRunnerProtocol]]
    engine_manufacturers_runner: Callable[[Path, bool], None]


@dataclass(frozen=True, slots=True)
class LayerOneRuntimeDependencies:
    run_config: RunConfig
    base_wiki_dir: Path
    runner_map: dict[str, LayerOneRunnerProtocol]
    run_id: str


class LayerOneExecutor:
    def __init__(
        self,
        *,
        seed_registry: tuple[SeedRegistryEntry, ...],
        dependencies: LayerOneExecutorDependencies,
    ) -> None:
        self._seed_registry = seed_registry
        self._dependencies = dependencies
        self._logger = get_logger(self.__class__.__name__)

    def run(self, run_config: RunConfig, base_wiki_dir: Path) -> None:
        self._dependencies.validate_seed_registry_function(self._seed_registry)
        runtime = LayerOneRuntimeDependencies(
            run_config=run_config,
            base_wiki_dir=base_wiki_dir,
            runner_map=self._dependencies.runner_map_builder(),
            run_id=str(uuid4()),
        )

        for seed in self._seed_registry:
            context = build_execution_context(
                run_id=runtime.run_id,
                seed_name=seed.seed_name,
                domain=seed.output_category,
                source_name=seed.complete_scraper_cls.__name__,
            )
            self._logger.info("layer1 seed started", extra=context)

            runner = runtime.runner_map.get(seed.seed_name)
            if runner is None:
                self._logger.warning("layer1 seed skipped: unsupported", extra=context)
                continue

            runner.run(seed, runtime.run_config, runtime.base_wiki_dir)
            self._logger.info("layer1 seed finished", extra=context)

        self._dependencies.engine_manufacturers_runner(
            base_wiki_dir=runtime.base_wiki_dir,
            include_urls=runtime.run_config.include_urls,
        )
