from __future__ import annotations

from collections.abc import Callable

from layers.constructors_mirror_service import ConstructorsMirrorService
from layers.one.executor import LayerOneExecutor
from layers.seed.registry.entries import ListJobRegistryEntry
from layers.zero.executor import LayerZeroExecutor as _LayerZeroExecutor
from layers.zero.merge_service import LayerZeroMergeService
from layers.zero.policies import MirrorConstructorsJobHook


class LayerZeroExecutor(_LayerZeroExecutor):
    """Compatibility wrapper preserving legacy constructor arguments."""

    def __init__(
        self,
        *,
        list_job_registry,
        validate_list_registry,
        run_config_factory_map_builder,
        default_config_factory,
        run_and_export_function,
        merge_service: LayerZeroMergeService,
        constructors_mirror_service: ConstructorsMirrorService,
        current_constructors_scraper_name: str,
        year_provider: Callable[[], int],
    ) -> None:
        super().__init__(
            list_job_registry=list_job_registry,
            validate_list_registry=validate_list_registry,
            run_config_factory_map_builder=run_config_factory_map_builder,
            default_config_factory=default_config_factory,
            run_and_export_function=run_and_export_function,
            merge_service=merge_service,
            job_hook=MirrorConstructorsJobHook(
                constructors_mirror_service=constructors_mirror_service,
                should_mirror_predicate=lambda job: job.list_scraper_cls.__name__
                == current_constructors_scraper_name,
            ),
            year_provider=year_provider,
        )


__all__ = [
    "ConstructorsMirrorService",
    "LayerOneExecutor",
    "LayerZeroExecutor",
    "LayerZeroMergeService",
    "ListJobRegistryEntry",
]
