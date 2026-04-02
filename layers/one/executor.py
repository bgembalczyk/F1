from collections.abc import Callable
from pathlib import Path
from uuid import uuid4

from layers.orchestration.contracts import LayerExecutionRequestDTO
from layers.orchestration.contracts import LayerExecutionResultDTO
from layers.orchestration.protocols import LayerOneRunnerProtocol
from layers.seed.registry.entries import SeedRegistryEntry
from scrapers.base.logging import build_execution_context
from scrapers.base.logging import get_logger
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
        engine_manufacturers_runner: Callable[[Path, bool], None],
    ) -> None:
        self._seed_registry = seed_registry
        self._validate_seed_registry_function = validate_seed_registry_function
        self._runner_map_builder = runner_map_builder
        self._engine_manufacturers_runner = engine_manufacturers_runner
        self._logger = get_logger(self.__class__.__name__)

    def run(
        self,
        request: LayerExecutionRequestDTO | RunConfig,
        base_wiki_dir: Path | None = None,
    ) -> LayerExecutionResultDTO:
        request_dto = self._coerce_run_request(request, base_wiki_dir)
        request_dto.validate()
        self._logger.info("layer1 run request: %s", request_dto.short())
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
            self._logger.info("layer1 seed started %s", request_dto.short(), extra=context)

            runner = runner_map.get(seed.seed_name)
            if runner is None:
                self._logger.warning("layer1 seed skipped: unsupported", extra=context)
                continue

            runner.run(seed, request_dto.run_config, request_dto.base_wiki_dir)
            self._logger.info("layer1 seed finished", extra=context)

        self._engine_manufacturers_runner(
            base_wiki_dir=request_dto.base_wiki_dir,
            include_urls=request_dto.run_config.include_urls,
        )
        result = LayerExecutionResultDTO(processed_jobs=len(self._seed_registry))
        self._logger.info("layer1 run finished: %s", result.short())
        return result

    def _coerce_run_request(
        self,
        request: LayerExecutionRequestDTO | RunConfig,
        base_wiki_dir: Path | None,
    ) -> LayerExecutionRequestDTO:
        if isinstance(request, LayerExecutionRequestDTO):
            return request
        if base_wiki_dir is None:
            msg = "base_wiki_dir is required for compatibility run_config calls"
            raise TypeError(msg)
        return LayerExecutionRequestDTO(run_config=request, base_wiki_dir=base_wiki_dir)
