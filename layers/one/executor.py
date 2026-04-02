import logging
from collections.abc import Callable
from pathlib import Path

from layers.orchestration.pipeline_trace import PipelineTrace
from layers.orchestration.protocols import LayerOneRunnerProtocol
from layers.seed.registry.entries import SeedRegistryEntry
from scrapers.base.run_config import RunConfig


LOGGER = logging.getLogger(__name__)


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
        engine_manufacturers_runner: Callable[[Path, bool], None],
        pipeline_trace: PipelineTrace,
    ) -> None:
        self._seed_registry = seed_registry
        self._validate_seed_registry_function = validate_seed_registry_function
        self._runner_map_builder = runner_map_builder
        self._engine_manufacturers_runner = engine_manufacturers_runner
        self._pipeline_trace = pipeline_trace

    def run(self, run_config: RunConfig, base_wiki_dir: Path) -> None:
        self._validate_seed_registry_function(self._seed_registry)
        runner_map = self._runner_map_builder()

        for seed in self._seed_registry:
            LOGGER.info("Layer one: running %s", seed.seed_name)
            self._pipeline_trace.start_job(layer="layer_one", job=seed.seed_name)

            runner = runner_map.get(seed.seed_name)
            if runner is None:
                self._pipeline_trace.skip_job(
                    layer="layer_one",
                    job=seed.seed_name,
                    reason="unsupported_seed",
                )
                LOGGER.info("Layer one: skipping unsupported seed %s", seed.seed_name)
                continue

            runner.run(seed, run_config, base_wiki_dir)
            self._pipeline_trace.end_job(layer="layer_one", job=seed.seed_name)
            LOGGER.info("Layer one: finished %s", seed.seed_name)

        self._engine_manufacturers_runner(
            base_wiki_dir=base_wiki_dir,
            include_urls=run_config.include_urls,
        )
