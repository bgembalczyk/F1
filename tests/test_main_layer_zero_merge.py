import json
from pathlib import Path

from scrapers.wiki.layer_zero_merge import merge_layer_zero_raw_outputs


def _write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload), encoding="utf-8")


def test_merge_layer_zero_raw_outputs_merges_and_transforms_domain_json_files(
    tmp_path: Path,
) -> None:
    base_wiki_dir = tmp_path / "data" / "wiki"

    _write_json(
        base_wiki_dir / "layers" / "0_layer" / "circuits" / "raw" / "a.json",
        [{"circuit": "Monza"}],
    )
    _write_json(
        base_wiki_dir / "layers" / "0_layer" / "constructors" / "raw" / "a.json",
        [{"constructor": "Ferrari"}],
    )
    _write_json(
        base_wiki_dir
        / "layers"
        / "0_layer"
        / "drivers"
        / "raw"
        / "female_drivers.json",
        [{"driver": "Maria"}],
    )
    _write_json(
        base_wiki_dir
        / "layers"
        / "0_layer"
        / "drivers"
        / "raw"
        / "f1_driver_fatalities.json",
        [{"driver": "X", "date": "2000-01-01", "event": "test"}],
    )
    _write_json(
        base_wiki_dir
        / "layers"
        / "0_layer"
        / "races"
        / "raw"
        / "f1_red_flagged_world_championship_races.json",
        [{"season": 1971, "grand_prix": "Canadian", "lap": 64}],
    )
    _write_json(
        base_wiki_dir
        / "layers"
        / "0_layer"
        / "races"
        / "raw"
        / "f1_red_flagged_non_championship_races.json",
        [{"season": 1971, "event": "Victory Race", "lap": 15}],
    )
    _write_json(
        base_wiki_dir / "layers" / "0_layer" / "rules" / "raw" / "a.json",
        [{"rule": "X"}],
    )
    _write_json(
        base_wiki_dir / "layers" / "0_layer" / "points" / "raw" / "a.json",
        [{"points": "X"}],
    )

    merge_layer_zero_raw_outputs(base_wiki_dir)

    circuits_merged = json.loads(
        (base_wiki_dir / "layers" / "0_layer" / "circuits" / "circuits.json").read_text(
            encoding="utf-8",
        ),
    )
    constructors_merged = json.loads(
        (
            base_wiki_dir
            / "layers"
            / "0_layer"
            / "constructors"
            / "constructors.json"
        ).read_text(
            encoding="utf-8",
        ),
    )
    drivers_merged = json.loads(
        (base_wiki_dir / "layers" / "0_layer" / "drivers" / "drivers.json").read_text(
            encoding="utf-8",
        ),
    )
    races_merged = json.loads(
        (base_wiki_dir / "layers" / "0_layer" / "races" / "races.json").read_text(
            encoding="utf-8",
        ),
    )

    assert circuits_merged == [{"circuit": "Monza", "series": ["Formula One"]}]
    assert constructors_merged == [
        {
            "constructor": "Ferrari",
            "status": "active",
            "series": ["Formula One"],
        },
    ]

    female_driver = next(item for item in drivers_merged if item["driver"] == "Maria")
    assert female_driver["gender"] == "female"

    fatality_driver = next(item for item in drivers_merged if item["driver"] == "X")
    assert fatality_driver["fatality"] == {"date": "2000-01-01", "event": "test"}

    world_race = next(item for item in races_merged if "grand_prix" in item)
    assert world_race["non_championship"] == "true"
    assert world_race["red_flag"] == {"lap": 64, "non_championship": "true"}

    non_champ_race = next(item for item in races_merged if "event" in item)
    assert non_champ_race["red_flag"] == {"lap": 15}

    assert not (base_wiki_dir / "layers" / "0_layer" / "rules" / "rules.json").exists()
    assert not (base_wiki_dir / "layers" / "0_layer" / "points" / "points.json").exists()
