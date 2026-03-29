from collections.abc import Callable
from pathlib import Path

from layers.orchestration.progress_reporter import ProgressReporter
from layers.seed.registry.entries import SeedRegistryEntry
from scrapers.base.run_config import RunConfig


class LayerOneExecutor:
    def __init__(
        self,
        *,
        seed_registry: tuple[SeedRegistryEntry, ...],
        validate_seed_registry_function: Callable[
            [tuple[SeedRegistryEntry, ...]],
            None,
        ],
        runner_map_builder: Callable[[], dict[str, object]],
        engine_manufacturers_runner: Callable[[Path, bool], None],
        progress_reporter: ProgressReporter,
    ) -> None:
        self._seed_registry = seed_registry
        self._validate_seed_registry_function = validate_seed_registry_function
        self._runner_map_builder = runner_map_builder
        self._engine_manufacturers_runner = engine_manufacturers_runner
        self._progress_reporter = progress_reporter

    def run(self, run_config: RunConfig, base_wiki_dir: Path) -> None:
        self._validate_seed_registry_function(self._seed_registry)
        runner_map = self._runner_map_builder()

        for seed in self._seed_registry:
            self._progress_reporter.started("complete", seed.seed_name)

            runner = runner_map.get(seed.seed_name)
            if runner is None:
                self._progress_reporter.skipped(
                    "complete",
                    seed.seed_name,
                    "unsupported seed",
                )
                continue

            runner.run(seed, run_config, base_wiki_dir)
            self._progress_reporter.finished("complete", seed.seed_name)

        self._engine_manufacturers_runner(
            base_wiki_dir=base_wiki_dir,
            include_urls=run_config.include_urls,
        )
