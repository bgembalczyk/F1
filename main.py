import json
import shutil
from datetime import datetime
from datetime import timezone
from pathlib import Path

from infrastructure.gemini.client import GeminiClient
from scrapers.base.helpers.runner import run_and_export
from scrapers.base.run_config import RunConfig
from scrapers.circuits.helpers.export import export_complete_circuits
from scrapers.data_paths import default_data_paths
from scrapers.constructors.helpers.export import export_complete_constructors
from scrapers.drivers.helpers.export import export_complete_drivers
from scrapers.engines.helpers.export import export_complete_engine_manufacturers
from scrapers.grands_prix.complete_scraper import F1CompleteGrandPrixDataExtractor
from scrapers.seasons.helpers import export_complete_seasons
from scrapers.sponsorship_liveries.helpers.paren_classifier import ParenClassifier
from scrapers.wiki.seed_l0 import compute_seed_quality
from scrapers.wiki.seed_l0 import normalize_seed_records
from scrapers.wiki.seed_l0 import write_seed_l0
from scrapers.wiki.seed_registry import WIKI_LIST_JOB_REGISTRY
from scrapers.wiki.seed_registry import WIKI_SEED_REGISTRY
from scrapers.wiki.seed_registry import validate_list_job_registry
from scrapers.wiki.seed_registry import validate_seed_registry

DATA_PATHS = default_data_paths()
BASE_RAW_DIR = DATA_PATHS.raw_root.resolve()
BASE_NORMALIZED_DIR = DATA_PATHS.normalized_root.resolve()
BASE_WIKI_DIR = DATA_PATHS.legacy_wiki_root.resolve()
BASE_DEBUG_DIR = Path("data/debug").resolve()
CURRENT_YEAR = datetime.now(tz=timezone.utc).year


def _write_legacy_compatibility_copy(source_path: Path, relative_path: str) -> Path:
    compatibility_path = BASE_WIKI_DIR / relative_path
    compatibility_path.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source_path, compatibility_path)
    return compatibility_path


def run_list_scrapers() -> None:
    run_config = RunConfig(
        output_dir=BASE_RAW_DIR,
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
            output_dir=BASE_RAW_DIR,
            include_urls=True,
            debug_dir=BASE_DEBUG_DIR,
            scraper_kwargs=scraper_kwargs,
        )

        run_and_export(
            job.list_scraper_cls,
            rendered_json_path,
            job.csv_output_path,
            run_config=local_run_config if scraper_kwargs else run_config,
        )

        try:
            seed_data_path = BASE_RAW_DIR / rendered_json_path
            legacy_raw_copy = _write_legacy_compatibility_copy(
                seed_data_path,
                rendered_json_path,
            )
            if job.csv_output_path:
                csv_source = BASE_RAW_DIR / job.csv_output_path
                _write_legacy_compatibility_copy(csv_source, job.csv_output_path)

            raw_seed_records = json.loads(seed_data_path.read_text(encoding="utf-8"))
            normalized_seed_records = normalize_seed_records(
                raw_seed_records,
                source_url=job.wikipedia_url,
            )
            l0_path = write_seed_l0(
                records=normalized_seed_records,
                category=job.output_category,
                seed_name=job.seed_name,
                output_root=BASE_RAW_DIR,
            )
            compatibility_path = write_seed_l0(
                records=normalized_seed_records,
                category=job.output_category,
                seed_name=job.seed_name,
                output_root=BASE_WIKI_DIR,
            )
            quality_report = compute_seed_quality(
                normalized_seed_records,
                seed_name=job.seed_name,
                category=job.output_category,
            )
            print(quality_report.to_log_line())
            print(f"[seed-l0] wrote {l0_path}")
            print(f"[seed-l0] compatibility copy {compatibility_path}")
            print(f"[list] compatibility copy {legacy_raw_copy}")
        except (OSError, ValueError, TypeError) as exc:
            print(f"[seed-l0] skip {job.seed_name}: {exc}")

        print(f"[list] finished {job.list_scraper_cls.__name__}")


def run_complete_scrapers() -> None:
    run_config = RunConfig(
        output_dir=BASE_NORMALIZED_DIR,
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
                output_dir=BASE_NORMALIZED_DIR / seed.default_output_path,
                include_urls=True,
            )
        elif seed.seed_name == "drivers":
            export_complete_drivers(
                output_dir=BASE_NORMALIZED_DIR / seed.default_output_path,
                include_urls=True,
            )
        elif seed.seed_name == "seasons":
            export_complete_seasons(
                output_dir=BASE_NORMALIZED_DIR / seed.default_output_path,
                include_urls=True,
            )
        elif seed.seed_name == "constructors":
            export_complete_constructors(
                output_dir=BASE_NORMALIZED_DIR / seed.default_output_path,
                include_urls=True,
            )

        print(f"[complete] finished {seed.seed_name}")

    print("[complete] running  F1CompleteEngineManufacturerDataExtractor")
    export_complete_engine_manufacturers(
        output_dir=BASE_NORMALIZED_DIR / "engines/complete_engine_manufacturers",
        include_urls=True,
    )
    print("[complete] finished F1CompleteEngineManufacturerDataExtractor")


def main() -> None:
    run_list_scrapers()
    run_complete_scrapers()


if __name__ == "__main__":
    main()
