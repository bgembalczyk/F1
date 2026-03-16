from datetime import datetime
from datetime import timezone
from pathlib import Path

from infrastructure.gemini.client import GeminiClient
from scrapers.base.helpers.runner import run_and_export
from scrapers.base.run_config import RunConfig
from scrapers.circuits.helpers.export import export_complete_circuits
from scrapers.constructors.helpers.export import export_complete_constructors
from scrapers.drivers.helpers.export import export_complete_drivers
from scrapers.engines.helpers.export import export_complete_engine_manufacturers
from scrapers.grands_prix.complete_scraper import F1CompleteGrandPrixDataExtractor
from scrapers.seasons.helpers import export_complete_seasons
from scrapers.sponsorship_liveries.helpers.paren_classifier import ParenClassifier
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

    for job in WIKI_LIST_JOB_REGISTRY:
        print(f"[list] running  {job.list_scraper_cls.__name__}")

        scraper_kwargs: dict[str, object] = {}
        if job.seed_name == "sponsorship_liveries":
            try:
                _gemini_client = GeminiClient.from_key_file()
                _classifier = ParenClassifier(_gemini_client)
                scraper_kwargs["classifier"] = _classifier
                print(
                    "[main] Gemini ParenClassifier załadowany - "
                    "adnotacje w nawiasach będą klasyfikowane.",
                )
            except FileNotFoundError as _e:
                print(
                    "[main] Brak klucza Gemini API "
                    f"({_e}), klasyfikacja Gemini wyłączona.",
                )

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


def run_layer_one() -> None:
    run_config = RunConfig(
        output_dir=BASE_WIKI_DIR,
        include_urls=True,
        debug_dir=BASE_DEBUG_DIR,
    )

    validate_seed_registry(WIKI_SEED_REGISTRY)

    for seed in WIKI_SEED_REGISTRY:
        print(f"[complete] running  {seed.seed_name}")

        if seed.seed_name == "grands_prix":
            run_and_export(
                F1CompleteGrandPrixDataExtractor,
                seed.default_output_path,
                run_config=run_config,
            )
        elif seed.seed_name == "circuits":
            export_complete_circuits(
                output_dir=BASE_WIKI_DIR / seed.default_output_path,
                include_urls=True,
            )
        elif seed.seed_name == "drivers":
            export_complete_drivers(
                output_dir=BASE_WIKI_DIR / seed.default_output_path,
                include_urls=True,
            )
        elif seed.seed_name == "seasons":
            export_complete_seasons(
                output_dir=BASE_WIKI_DIR / seed.default_output_path,
                include_urls=True,
            )
        elif seed.seed_name == "constructors":
            export_complete_constructors(
                output_dir=BASE_WIKI_DIR / seed.default_output_path,
                include_urls=True,
            )

        print(f"[complete] finished {seed.seed_name}")

    print("[complete] running  F1CompleteEngineManufacturerDataExtractor")
    export_complete_engine_manufacturers(
        output_dir=BASE_WIKI_DIR / "engines/complete_engine_manufacturers",
        include_urls=True,
    )
    print("[complete] finished F1CompleteEngineManufacturerDataExtractor")


def main() -> None:
    run_layer_zero()


if __name__ == "__main__":
    main()
