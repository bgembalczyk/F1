from collections.abc import Callable
from pathlib import Path
from typing import Protocol
from typing import cast

from layers.constructors_mirror_service import ConstructorsMirrorService
from layers.orchestration.factories import LayerZeroRunConfigFactoryProtocol
from layers.seed.registry.entries import ListJobRegistryEntry
from layers.zero.helpers import layer_zero_raw_paths
from layers.zero.merge_service import LayerZeroMergeService
from scrapers.base.abc import ABCScraper
from scrapers.base.run_config import RunConfig


class RunAndExportFunctionProtocol(Protocol):
    def __call__(
        self,
        scraper_cls: type[ABCScraper],
        json_rel: str | Path,
        csv_rel: str | Path | None = None,
        *,
        run_config: RunConfig,
        supports_urls: bool = True,
    ) -> None: ...


class LayerZeroExecutor:
    def __init__(
        self,
        *,
        list_job_registry: tuple[ListJobRegistryEntry, ...],
        validate_list_registry: Callable[[tuple[ListJobRegistryEntry, ...]], None],
        run_config_factory_map_builder: Callable[
            [],
            dict[str, LayerZeroRunConfigFactoryProtocol],
        ],
        default_config_factory: LayerZeroRunConfigFactoryProtocol,
        run_and_export_function: RunAndExportFunctionProtocol,
        constructors_mirror_service: ConstructorsMirrorService,
        merge_service: LayerZeroMergeService,
        current_constructors_scraper_name: str,
        year_provider: Callable[[], int],
    ) -> None:
        self._list_job_registry = list_job_registry
        self._validate_list_registry = validate_list_registry
        self._run_config_factory_map_builder = run_config_factory_map_builder
        self._default_config_factory = default_config_factory
        self._run_and_export_function = run_and_export_function
        self._constructors_mirror_service = constructors_mirror_service
        self._merge_service = merge_service
        self._current_constructors_scraper_name = current_constructors_scraper_name
        self._year_provider = year_provider

    def run(self, run_config: RunConfig, base_wiki_dir: Path) -> None:
        self._validate_list_registry(self._list_job_registry)

        config_factories = self._run_config_factory_map_builder()

        for job in self._list_job_registry:
            list_scraper_cls = cast(type[ABCScraper], job.list_scraper_cls)
            print(f"[list] running  {list_scraper_cls.__name__}")

            config_factory = config_factories.get(
                job.seed_name,
                self._default_config_factory,
            )
            scraper_kwargs = config_factory.create_scraper_kwargs(job)

            rendered_json_path = job.json_output_path.format(year=self._year_provider())
            local_run_config = RunConfig(
                output_dir=run_config.output_dir,
                include_urls=run_config.include_urls,
                debug_dir=run_config.debug_dir,
                scraper_kwargs=scraper_kwargs,
            )

            l0_raw_json_path, l0_raw_csv_path = layer_zero_raw_paths(
                output_category=job.output_category,
                rendered_json_path=rendered_json_path,
                csv_output_path=job.csv_output_path,
            )

            self._run_and_export_function(
                list_scraper_cls,
                l0_raw_json_path,
                l0_raw_csv_path,
                run_config=local_run_config if scraper_kwargs else run_config,
            )

            if list_scraper_cls.__name__ == self._current_constructors_scraper_name:
                source_json_path = base_wiki_dir / l0_raw_json_path
                self._constructors_mirror_service.mirror(
                    base_wiki_dir,
                    source_json_path,
                )

            print(f"[list] finished {list_scraper_cls.__name__}")

        self._merge_service.merge(base_wiki_dir)
