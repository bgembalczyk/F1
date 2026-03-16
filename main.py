from datetime import datetime
from datetime import timezone
from pathlib import Path

from scrapers.base.helpers.runner import run_and_export
from scrapers.base.run_config import RunConfig
from scrapers.wiki.layer_zero_merge import merge_layer_zero_raw_outputs
from scrapers.wiki.orchestration import DefaultLayerZeroRunConfigFactory
from scrapers.wiki.orchestration import build_layer_one_runner_map
from scrapers.wiki.orchestration import build_layer_zero_run_config_factory_map
from scrapers.wiki.orchestration import run_engine_manufacturers
from scrapers.wiki.seed_registry import WIKI_LIST_JOB_REGISTRY
from scrapers.wiki.seed_registry import WIKI_SEED_REGISTRY
from scrapers.wiki.seed_registry import validate_list_job_registry
from scrapers.wiki.seed_registry import validate_seed_registry

# Ścieżki wyjściowe względem katalogu repo (ten plik jest w root)
BASE_WIKI_DIR = Path("data/wiki").resolve()
BASE_DEBUG_DIR = Path("data/debug").resolve()
CURRENT_YEAR = datetime.now(tz=timezone.utc).year


def run_layer_zero() -> None:
    run_config = RunConfig(
        output_dir=BASE_WIKI_DIR,
        include_urls=True,
        debug_dir=BASE_DEBUG_DIR,
    )

    validate_list_job_registry(WIKI_LIST_JOB_REGISTRY)

    config_factories = build_layer_zero_run_config_factory_map()
    default_factory = DefaultLayerZeroRunConfigFactory()

    for job in WIKI_LIST_JOB_REGISTRY:
        print(f"[list] running  {job.list_scraper_cls.__name__}")

        config_factory = config_factories.get(job.seed_name, default_factory)
        scraper_kwargs = config_factory.create_scraper_kwargs(job)

        rendered_json_path = job.json_output_path.format(year=CURRENT_YEAR)
        local_run_config = RunConfig(
            output_dir=BASE_WIKI_DIR,
            include_urls=True,
            debug_dir=BASE_DEBUG_DIR,
            scraper_kwargs=scraper_kwargs,
        )

        l0_raw_json_path = (
            Path("layers")
            / "0_layer"
            / job.output_category
            / "raw"
            / Path(rendered_json_path).name
        )
        l0_raw_csv_path: Path | None = None
        if job.csv_output_path:
            l0_raw_csv_path = (
                Path("layers")
                / "0_layer"
                / job.output_category
                / "raw"
                / Path(job.csv_output_path).name
            )

        run_and_export(
            job.list_scraper_cls,
            l0_raw_json_path,
            l0_raw_csv_path,
            run_config=local_run_config if scraper_kwargs else run_config,
        )

        print(f"[list] finished {job.list_scraper_cls.__name__}")

    merge_layer_zero_raw_outputs(BASE_WIKI_DIR)


def run_layer_one() -> None:
    run_config = RunConfig(
        output_dir=BASE_WIKI_DIR,
        include_urls=True,
        debug_dir=BASE_DEBUG_DIR,
    )

    validate_seed_registry(WIKI_SEED_REGISTRY)
    runner_map = build_layer_one_runner_map()

    for seed in WIKI_SEED_REGISTRY:
        print(f"[complete] running  {seed.seed_name}")

        runner = runner_map.get(seed.seed_name)
        if runner is None:
            print(f"[complete] skipping unsupported seed: {seed.seed_name}")
            continue

        runner.run(seed, run_config, BASE_WIKI_DIR)

        print(f"[complete] finished {seed.seed_name}")

    run_engine_manufacturers(base_wiki_dir=BASE_WIKI_DIR, include_urls=True)


def main() -> None:
    run_layer_zero()


if __name__ == "__main__":
    main()
