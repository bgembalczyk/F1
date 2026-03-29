from collections.abc import Callable
from pathlib import Path

from layers.orchestration.protocols import LayerOneRunnerProtocol
from layers.orchestration.reporter import PipelineStepReporterProtocol
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
        runner_map_builder: Callable[[], dict[str, LayerOneRunnerProtocol]],
        engine_manufacturers_runner: Callable[..., None],
        step_reporter: PipelineStepReporterProtocol,
    ) -> None:
        self._seed_registry = seed_registry
        self._validate_seed_registry_function = validate_seed_registry_function
        self._runner_map_builder = runner_map_builder
        self._engine_manufacturers_runner = engine_manufacturers_runner
        self._step_reporter = step_reporter

    def run(self, run_config: RunConfig, base_wiki_dir: Path) -> None:
        self._validate_seed_registry_function(self._seed_registry)
        runner_map = self._runner_map_builder()

        for seed in self._seed_registry:
            self._step_reporter.start(
                layer="layer_one",
                step_type="seed",
                step_name=seed.seed_name,
            )

            runner = runner_map.get(seed.seed_name)
            if runner is None:
                self._step_reporter.skip(
                    layer="layer_one",
                    step_type="seed",
                    step_name=seed.seed_name,
                    reason="unsupported-seed",
                )
                continue

            runner.run(seed, run_config, base_wiki_dir)
            self._step_reporter.finish(
                layer="layer_one",
                step_type="seed",
                step_name=seed.seed_name,
            )

        self._engine_manufacturers_runner(
            base_wiki_dir=base_wiki_dir,
            include_urls=run_config.include_urls,
            step_reporter=self._step_reporter,
        )
