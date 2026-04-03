from __future__ import annotations

import shutil
from dataclasses import dataclass
from datetime import datetime
from datetime import timezone
from enum import Enum
from typing import TYPE_CHECKING
from typing import Callable

from layers.constructors_mirror_service import ConstructorsMirrorService
from layers.one.executor import LayerOneExecutor
from layers.one.executor import LayerOneExecutorPreset
from layers.orchestration.factories import DefaultLayerZeroRunConfigFactory
from layers.orchestration.runner_registry import build_layer_one_runner_map
from layers.orchestration.runner_registry import build_layer_zero_run_config_factory_map
from layers.orchestration.runner_registry import run_engine_manufacturers
from layers.pipeline import WikiPipelineApplication
from layers.seed.registry.constants import WIKI_LIST_JOB_REGISTRY
from layers.seed.registry.helpers import get_wiki_seed_registry
from layers.seed.registry.helpers import validate_list_job_registry
from layers.seed.registry.helpers import validate_seed_registry
from layers.zero.executor import LayerZeroExecutor
from layers.zero.executor import LayerZeroExecutorPreset
from layers.zero.merge import merge_layer_zero_raw_outputs
from layers.zero.merge_service import LayerZeroMergeService
from layers.zero.policies import MirrorConstructorsJobHook
from layers.zero.policies import NullLayerZeroJobHook

if TYPE_CHECKING:
    from pathlib import Path


def _current_year() -> int:
    return datetime.now(tz=timezone.utc).year


def _should_mirror_constructors_job(job: object) -> bool:
    """Aktywna dla `CurrentConstructorsListScraper` i `ConstructorsListScraper`."""
    list_scraper_cls = getattr(job, "list_scraper_cls", None)
    scraper_name = getattr(list_scraper_cls, "__name__", "")
    return scraper_name in {"CurrentConstructorsListScraper", "ConstructorsListScraper"}


class ApplicationPresetName(str, Enum):
    DEFAULT = "default"
    DEBUG = "debug"
    MINIMAL = "minimal"


@dataclass(frozen=True)
class ApplicationPreset:
    layer_zero_preset: Callable[[], LayerZeroExecutorPreset]
    layer_one_preset: Callable[[], LayerOneExecutorPreset]


def _build_default_layer_zero_preset() -> LayerZeroExecutorPreset:
    return LayerZeroExecutorPreset(
        list_job_registry=WIKI_LIST_JOB_REGISTRY,
        validate_list_registry=validate_list_job_registry,
        config_factories=build_layer_zero_run_config_factory_map,
        default_config_factory=DefaultLayerZeroRunConfigFactory(),
        merger=LayerZeroMergeService(
            merge=merge_layer_zero_raw_outputs,
        ),
        job_hook=MirrorConstructorsJobHook(
            mirror=ConstructorsMirrorService(
                mirror_targets=(
                    ("chassis_constructors", "f1_constructors_{year}.json"),
                    ("constructors", "f1_constructors_{year}.json"),
                    ("teams", "f1_constructors_{year}.json"),
                ),
                copy_file=shutil.copy2,
                year_provider=_current_year,
            ),
            should_mirror_predicate=_should_mirror_constructors_job,
        ),
        year_provider=_current_year,
    )


def _build_minimal_layer_zero_preset() -> LayerZeroExecutorPreset:
    default_preset = _build_default_layer_zero_preset()
    return LayerZeroExecutorPreset(
        list_job_registry=default_preset.list_job_registry,
        validate_list_registry=default_preset.validate_list_registry,
        config_factories=default_preset.config_factories,
        default_config_factory=default_preset.default_config_factory,
        merger=default_preset.merger,
        job_hook=NullLayerZeroJobHook(),
        year_provider=default_preset.year_provider,
    )


def _build_default_layer_one_preset() -> LayerOneExecutorPreset:
    return LayerOneExecutorPreset(
        seed_registry=get_wiki_seed_registry(),
        validate_seed_registry=validate_seed_registry,
        runners=build_layer_one_runner_map,
        engine_manufacturers_runner=run_engine_manufacturers,
    )


APPLICATION_PRESETS: dict[ApplicationPresetName, ApplicationPreset] = {
    ApplicationPresetName.DEFAULT: ApplicationPreset(
        layer_zero_preset=_build_default_layer_zero_preset,
        layer_one_preset=_build_default_layer_one_preset,
    ),
    ApplicationPresetName.DEBUG: ApplicationPreset(
        layer_zero_preset=_build_default_layer_zero_preset,
        layer_one_preset=_build_default_layer_one_preset,
    ),
    ApplicationPresetName.MINIMAL: ApplicationPreset(
        layer_zero_preset=_build_minimal_layer_zero_preset,
        layer_one_preset=_build_default_layer_one_preset,
    ),
}


def create_default_wiki_pipeline_application(
    *,
    base_wiki_dir: Path,
    base_debug_dir: Path,
    preset: ApplicationPresetName = ApplicationPresetName.DEFAULT,
) -> WikiPipelineApplication:
    app_preset = APPLICATION_PRESETS[preset]
    layer_zero_executor = LayerZeroExecutor(preset=app_preset.layer_zero_preset())
    layer_one_executor = LayerOneExecutor(preset=app_preset.layer_one_preset())

    return WikiPipelineApplication(
        base_wiki_dir=base_wiki_dir,
        base_debug_dir=base_debug_dir,
        layer_zero_executor=layer_zero_executor,
        layer_one_executor=layer_one_executor,
    )
