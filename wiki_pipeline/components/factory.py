import shutil
from datetime import datetime
from datetime import timezone

from pathlib import Path

from layers.constructors_mirror_service import ConstructorsMirrorService
from layers.executors.one import LayerOneExecutor
from layers.executors.zero import LayerZeroExecutor
from layers.job_hooks.composite_zero import CompositeLayerZeroJobHook
from layers.job_hooks.mirror.constructors import MirrorConstructorsJobHook
from layers.job_hooks.mirror.to_domain_by_filename import MirrorToDomainByFilenameJobHook
from layers.orchestration.runner_registry import build_layer_one_runner_map
from layers.orchestration.runner_registry import build_layer_zero_run_config_factory_map
from layers.orchestration.runner_registry import run_engine_manufacturers
from layers.seed.registry.constants import WIKI_LIST_JOB_REGISTRY
from layers.seed.registry.helpers import get_wiki_seed_registry
from layers.seed.registry.helpers import validate_list_job_registry
from layers.seed.registry.helpers import validate_seed_registry
from layers.zero.d_merge import merge_layer_zero_phase_d
from layers.zero.extract import extract_layer_zero_phase_c
from layers.zero.merge import merge_layer_zero_raw_outputs
from layers.zero.merge_service import LayerZeroMergeService
from layers.zero.run_config_factories.default import DefaultLayerZeroRunConfigFactory
from wiki_pipeline.components.base import WikiPipelineComponents


class WikiPipelineComponentsFactory:
    @staticmethod
    def current_year() -> int:
        return datetime.now(tz=timezone.utc).year

    @staticmethod
    def should_mirror_constructors_job(job: object) -> bool:
        """Aktywna dla `constructors_current`."""
        list_scraper_cls = getattr(job, "list_scraper_cls", None)
        scraper_name = getattr(list_scraper_cls, "__name__", "")
        if scraper_name == "CurrentConstructorsListScraper":
            return True
        seed_name = getattr(job, "seed_name", "")
        return seed_name == "constructors_current"

    @staticmethod
    def should_mirror_points_job(job: object) -> bool:
        list_scraper_cls = getattr(job, "list_scraper_cls", None)
        scraper_name = getattr(list_scraper_cls, "__name__", "")
        if scraper_name == "PointsScraper":
            return True
        seed_name = getattr(job, "seed_name", "")
        return seed_name in {"points_history", "points_shortened", "points_sprint"}

    @staticmethod
    def should_mirror_engine_rules_job(job: object) -> bool:
        list_scraper_cls = getattr(job, "list_scraper_cls", None)
        scraper_name = getattr(list_scraper_cls, "__name__", "")
        if scraper_name in {"EngineRegulationScraper", "EngineRestrictionsScraper"}:
            return True
        seed_name = getattr(job, "seed_name", "")
        return seed_name in {"engines_regulations", "engines_restrictions"}

    @staticmethod
    def run_layer_zero_phases(base_wiki_dir: Path) -> None:
        merge_layer_zero_raw_outputs(base_wiki_dir)
        extract_layer_zero_phase_c(base_wiki_dir)
        merge_layer_zero_phase_d(base_wiki_dir)

    @classmethod
    def build_components(cls) -> WikiPipelineComponents:
        layer_zero_merge_service = LayerZeroMergeService(
            merge=cls.run_layer_zero_phases,
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
                            year_provider=cls.current_year,
                        ),
                        should_mirror_predicate=cls.should_mirror_constructors_job,
                    ),
                    MirrorToDomainByFilenameJobHook(
                        target_domain="seasons",
                        should_mirror_predicate=cls.should_mirror_points_job,
                    ),
                    MirrorToDomainByFilenameJobHook(
                        target_domain="seasons",
                        should_mirror_predicate=cls.should_mirror_engine_rules_job,
                    ),
                ),
            ),
            year_provider=cls.current_year,
        )

        layer_one_executor = LayerOneExecutor(
            seed_registry=get_wiki_seed_registry(),
            validate_seed_registry=validate_seed_registry,
            runners=build_layer_one_runner_map,
            engine_manufacturers_runner=run_engine_manufacturers,
        )

        return WikiPipelineComponents(
            layer_zero_executor=layer_zero_executor,
            layer_one_executor=layer_one_executor,
            layer_zero_merge_service=layer_zero_merge_service,
        )
