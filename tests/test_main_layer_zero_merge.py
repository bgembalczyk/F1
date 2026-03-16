import json
from pathlib import Path

from scrapers.wiki.layer_zero_merge import merge_layer_zero_raw_outputs


def _write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload), encoding="utf-8")


def test_merge_layer_zero_raw_outputs_merges_all_domain_json_files(tmp_path: Path) -> None:
    base_wiki_dir = tmp_path / "data" / "wiki"

    _write_json(
        base_wiki_dir / "layers" / "0_layer" / "drivers" / "raw" / "a.json",
        [{"id": 1}, {"id": 2}],
    )
    _write_json(
        base_wiki_dir / "layers" / "0_layer" / "drivers" / "raw" / "b.json",
        {"id": 3},
    )
    _write_json(
        base_wiki_dir
        / "layers"
        / "0_layer"
        / "rules"
        / "raw"
        / "nested"
        / "c.json",
        [{"rule": "X"}],
    )

    merge_layer_zero_raw_outputs(base_wiki_dir)

    drivers_merged = json.loads(
        (base_wiki_dir / "layers" / "0_layer" / "drivers" / "merged.json").read_text(
            encoding="utf-8",
        ),
    )
    rules_merged = json.loads(
        (base_wiki_dir / "layers" / "0_layer" / "rules" / "merged.json").read_text(
            encoding="utf-8",
        ),
    )

    assert drivers_merged == [{"id": 1}, {"id": 2}, {"id": 3}]
    assert rules_merged == [{"rule": "X"}]
