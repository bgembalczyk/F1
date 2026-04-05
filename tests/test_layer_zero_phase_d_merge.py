# ruff: noqa: PLR2004
from __future__ import annotations

import json
from pathlib import Path

from layers.zero.d_merge import merge_layer_zero_phase_d


def _write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload), encoding="utf-8")


def _c_extract_path(base: Path, domain: str) -> Path:
    return base / "layers" / "0_layer" / domain / "C_extract"


def _d_merge_path(base: Path, domain: str) -> Path:
    return base / "layers" / "0_layer" / domain / "D_merge"


class TestMergeLayerZeroPhaseD:
    def test_merges_multiple_c_extract_files_into_d_merge(self, tmp_path: Path) -> None:
        base = tmp_path / "data" / "wiki"
        _write_json(
            _c_extract_path(base, "countries") / "from_circuits.json",
            [{"text": "Italy", "url": "https://en.wikipedia.org/wiki/Italy"}],
        )
        _write_json(
            _c_extract_path(base, "countries") / "from_drivers.json",
            ["Italy", "Germany"],
        )

        merge_layer_zero_phase_d(base)

        d_merge_file = _d_merge_path(base, "countries") / "countries.json"
        assert d_merge_file.exists()
        result = json.loads(d_merge_file.read_text(encoding="utf-8"))
        assert len(result) == 3

    def test_deduplicates_by_url(self, tmp_path: Path) -> None:
        base = tmp_path / "data" / "wiki"
        italy = {"text": "Italy", "url": "https://en.wikipedia.org/wiki/Italy"}
        _write_json(
            _c_extract_path(base, "countries") / "a.json",
            [italy],
        )
        _write_json(
            _c_extract_path(base, "countries") / "b.json",
            [italy, {"text": "France", "url": "https://en.wikipedia.org/wiki/France"}],
        )

        merge_layer_zero_phase_d(base)

        result = json.loads(
            (_d_merge_path(base, "countries") / "countries.json").read_text(encoding="utf-8")
        )
        assert len(result) == 2

    def test_deduplicates_strings(self, tmp_path: Path) -> None:
        base = tmp_path / "data" / "wiki"
        _write_json(
            _c_extract_path(base, "countries") / "from_drivers.json",
            ["Italy", "Germany", "Italy"],
        )

        merge_layer_zero_phase_d(base)

        result = json.loads(
            (_d_merge_path(base, "countries") / "countries.json").read_text(encoding="utf-8")
        )
        assert result.count("Italy") == 1

    def test_does_nothing_if_layer_zero_dir_missing(self, tmp_path: Path) -> None:
        merge_layer_zero_phase_d(tmp_path / "nonexistent")

    def test_skips_domain_without_c_extract(self, tmp_path: Path) -> None:
        base = tmp_path / "data" / "wiki"
        (base / "layers" / "0_layer" / "circuits").mkdir(parents=True)

        merge_layer_zero_phase_d(base)

        assert not _d_merge_path(base, "circuits").exists()

    def test_produces_d_merge_for_existing_domain_with_single_file(
        self, tmp_path: Path
    ) -> None:
        base = tmp_path / "data" / "wiki"
        payload = [{"text": "Monza", "url": "https://en.wikipedia.org/wiki/Monza"}]
        _write_json(_c_extract_path(base, "locations") / "from_circuits.json", payload)

        merge_layer_zero_phase_d(base)

        d_merge_file = _d_merge_path(base, "locations") / "locations.json"
        assert d_merge_file.exists()
        result = json.loads(d_merge_file.read_text(encoding="utf-8"))
        assert result == payload
