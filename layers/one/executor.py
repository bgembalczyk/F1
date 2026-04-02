from collections.abc import Callable
from uuid import uuid4

from layers.orchestration.protocols import LayerOneRunnerProtocol
from layers.orchestration.runtime_config import RuntimeConfig
from layers.seed.registry.entries import SeedRegistryEntry
from scrapers.base.logging import build_execution_context
from scrapers.base.logging import get_logger


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
        engine_manufacturers_runner: Callable[[RuntimeConfig], None],
    ) -> None:
        self._seed_registry = seed_registry
        self._validate_seed_registry_function = validate_seed_registry_function
        self._runner_map_builder = runner_map_builder
        self._engine_manufacturers_runner = engine_manufacturers_runner
        self._logger = get_logger(self.__class__.__name__)

    def run(self, runtime_config: RuntimeConfig) -> None:
        self._validate_seed_registry_function(self._seed_registry)
        runner_map = self._runner_map_builder()
        run_id = str(uuid4())

        for seed in self._seed_registry:
            context = build_execution_context(
                run_id=run_id,
                seed_name=seed.seed_name,
                domain=seed.output_category,
                source_name=seed.complete_scraper_cls.__name__,
            )
            self._logger.info("layer1 seed started", extra=context)

            runner = runner_map.get(seed.seed_name)
            if runner is None:
                self._logger.warning("layer1 seed skipped: unsupported", extra=context)
                continue

            runner.run(seed, runtime_config)
            self._logger.info("layer1 seed finished", extra=context)

        self._engine_manufacturers_runner(runtime_config)
