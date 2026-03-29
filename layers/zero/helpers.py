from pathlib import Path

from scrapers.base.run_config import RunConfig
from scrapers.base.run_profiles import RunPathConfig
from scrapers.base.run_profiles import RunProfileName
from scrapers.base.run_profiles import build_run_profile


def build_debug_run_config(*, base_wiki_dir: Path, base_debug_dir: Path) -> RunConfig:
    return build_run_profile(
        RunProfileName.DEBUG,
        paths=RunPathConfig(
            wiki_output_dir=base_wiki_dir,
            debug_dir=base_debug_dir,
        ),
    )


def layer_zero_raw_paths(
    *,
    output_category: str,
    rendered_json_path: str,
    csv_output_path: str | None,
) -> tuple[Path, Path | None]:
    json_path = _build_raw_path(output_category, rendered_json_path)
    csv_path: Path | None = None
    if csv_output_path:
        csv_path = _build_raw_path(output_category, csv_output_path)
    return json_path, csv_path


def _build_raw_path(output_category: str, filename: str) -> Path:
    return Path("layers") / "0_layer" / output_category / "raw" / Path(filename).name
