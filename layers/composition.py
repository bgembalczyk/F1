from __future__ import annotations

import shutil
from datetime import datetime
from datetime import timezone
from typing import TYPE_CHECKING

from layers.constructors_mirror_service import ConstructorsMirrorService
from layers.one.executor import LayerOneExecutor
from layers.orchestration.factories import DefaultLayerZeroRunConfigFactory
from layers.orchestration.runner_registry import build_layer_one_runner_map
from layers.orchestration.runner_registry import build_layer_zero_run_config_factory_map
from layers.orchestration.runner_registry import run_engine_manufacturers
from layers.pipeline import WikiPipelineApplication
from layers.seed.registry.constants import WIKI_LIST_JOB_REGISTRY
from layers.seed.registry.helpers import get_wiki_seed_registry
from layers.seed.registry.helpers import validate_list_job_registry
from layers.seed.registry.helpers import validate_seed_registry
from layers.zero.d_merge import merge_layer_zero_phase_d
from layers.zero.executor import LayerZeroExecutor
from layers.zero.extract import extract_layer_zero_phase_c
from layers.zero.merge import merge_layer_zero_raw_outputs
from layers.zero.merge_service import LayerZeroMergeService
from layers.zero.policies import CompositeLayerZeroJobHook
from layers.zero.policies import MirrorConstructorsJobHook
from layers.zero.policies import MirrorToDomainByFilenameJobHook

if TYPE_CHECKING:
    from pathlib import Path


def _current_year() -> int:
    return datetime.now(tz=timezone.utc).year


def _should_mirror_constructors_job(job: object) -> bool:
    """Aktywna dla `constructors_current`."""
    list_scraper_cls = getattr(job, "list_scraper_cls", None)
    scraper_name = getattr(list_scraper_cls, "__name__", "")
    if scraper_name == "CurrentConstructorsListScraper":
        return True
    seed_name = getattr(job, "seed_name", "")
    return seed_name == "constructors_current"


def _should_mirror_points_job(job: object) -> bool:
    list_scraper_cls = getattr(job, "list_scraper_cls", None)
    scraper_name = getattr(list_scraper_cls, "__name__", "")
    if scraper_name == "PointsScraper":
        return True
    seed_name = getattr(job, "seed_name", "")
    return seed_name in {"points_history", "points_shortened", "points_sprint"}


def _should_mirror_engine_rules_job(job: object) -> bool:
    list_scraper_cls = getattr(job, "list_scraper_cls", None)
    scraper_name = getattr(list_scraper_cls, "__name__", "")
    if scraper_name in {"EngineRegulationScraper", "EngineRestrictionsScraper"}:
        return True
    seed_name = getattr(job, "seed_name", "")
    return seed_name in {"engines_regulations", "engines_restrictions"}


def _run_layer_zero_phases(base_wiki_dir: Path) -> None:
    merge_layer_zero_raw_outputs(base_wiki_dir)
    extract_layer_zero_phase_c(base_wiki_dir)
    merge_layer_zero_phase_d(base_wiki_dir)


def create_default_wiki_pipeline_application(
    *,
    base_wiki_dir: Path,
    base_debug_dir: Path,
) -> WikiPipelineApplication:
    """Composition root dla domyślnej aplikacji wiki pipeline."""
    layer_zero_merge_service = LayerZeroMergeService(
        merge=_run_layer_zero_phases,
    )

    layer_zero_executor = LayerZeroExecutor(
        list_job_registry=WIKI_LIST_JOB_REGISTRY,
        validate_list_registry=validate_list_job_registry,
        config_factories=build_layer_zero_run_config_factory_map,
        default_config_factory=DefaultLayerZeroRunConfigFactory(),
        merger=layer_zero_merge_service,
        job_hook=CompositeLayerZeroJobHook(
            hooks=(
                MirrorConstructorsJobHook(
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
                MirrorToDomainByFilenameJobHook(
                    target_domain="seasons",
                    should_mirror_predicate=_should_mirror_points_job,
                ),
                MirrorToDomainByFilenameJobHook(
                    target_domain="seasons",
                    should_mirror_predicate=_should_mirror_engine_rules_job,
                ),
            ),
        ),
        year_provider=_current_year,
    )

    layer_one_executor = LayerOneExecutor(
        seed_registry=get_wiki_seed_registry(),
        validate_seed_registry=validate_seed_registry,
        runners=build_layer_one_runner_map,
        engine_manufacturers_runner=run_engine_manufacturers,
    )

    return WikiPipelineApplication(
        base_wiki_dir=base_wiki_dir,
        base_debug_dir=base_debug_dir,
        layer_zero_executor=layer_zero_executor,
        layer_one_executor=layer_one_executor,
        layer_zero_merge_service=LayerZeroMergeService(
            merge=_run_layer_zero_phases,
        ),
    )
