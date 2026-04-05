# ruff: noqa: PLR0915, PLR2004
import json
from pathlib import Path

from scrapers.wiki.layer_zero_merge import merge_layer_zero_raw_outputs
from tests.support.main_layer_zero_merge_helpers import _assert_merged_outputs
from tests.support.main_layer_zero_merge_helpers import _seed_layer_zero_raw_data


def test_merge_layer_zero_raw_outputs_merges_and_transforms_domain_json_files(
    tmp_path: Path,
) -> None:
    base_wiki_dir = tmp_path / "data" / "wiki"

    _seed_layer_zero_raw_data(base_wiki_dir)

    merge_layer_zero_raw_outputs(base_wiki_dir)

    circuits_merged = json.loads(
        (
            base_wiki_dir / "layers" / "0_layer" / "circuits" / "B_merge" / "circuits.json"
        ).read_text(encoding="utf-8"),
    )
    constructors_merged = json.loads(
        (
            base_wiki_dir
            / "layers"
            / "0_layer"
            / "constructors"
            / "B_merge"
            / "constructors.json"
        ).read_text(
            encoding="utf-8",
        ),
    )
    drivers_merged = json.loads(
        (
            base_wiki_dir / "layers" / "0_layer" / "drivers" / "B_merge" / "drivers.json"
        ).read_text(encoding="utf-8"),
    )
    races_merged = json.loads(
        (base_wiki_dir / "layers" / "0_layer" / "races" / "B_merge" / "races.json").read_text(
            encoding="utf-8",
        ),
    )
    engines_merged = json.loads(
        (
            base_wiki_dir / "layers" / "0_layer" / "engines" / "B_merge" / "engines.json"
        ).read_text(encoding="utf-8"),
    )
    grands_prix_merged = json.loads(
        (
            base_wiki_dir
            / "layers"
            / "0_layer"
            / "grands_prix"
            / "B_merge"
            / "grands_prix.json"
        ).read_text(encoding="utf-8"),
    )
    teams_merged = json.loads(
        (base_wiki_dir / "layers" / "0_layer" / "teams" / "B_merge" / "teams.json").read_text(
            encoding="utf-8",
        ),
    )
    seasons_merged = json.loads(
        (
            base_wiki_dir / "layers" / "0_layer" / "seasons" / "B_merge" / "seasons.json"
        ).read_text(encoding="utf-8"),
    )
    season_merged = json.loads(
        (base_wiki_dir / "layers" / "0_layer" / "season" / "B_merge" / "season.json").read_text(
            encoding="utf-8",
        ),
    )

    _assert_merged_outputs(
        circuits_merged=circuits_merged,
        constructors_merged=constructors_merged,
        drivers_merged=drivers_merged,
        races_merged=races_merged,
        engines_merged=engines_merged,
        grands_prix_merged=grands_prix_merged,
        teams_merged=teams_merged,
        seasons_merged=seasons_merged,
        season_merged=season_merged,
        base_wiki_dir=base_wiki_dir,
    )
