# ruff: noqa: PLR2004
from __future__ import annotations

import json
from typing import TYPE_CHECKING

from layers.zero.d_merge import merge_layer_zero_phase_d

if TYPE_CHECKING:
    from pathlib import Path


def write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload), encoding="utf-8")


def c_extract_path(base: Path, domain: str) -> Path:
    return base / "layers" / "0_layer" / domain / "C_extract"


def d_merge_path(base: Path, domain: str) -> Path:
    return base / "layers" / "0_layer" / domain / "D_merge"


class TestMergeLayerZeroPhaseD:
    def test_merges_multiple_c_extract_files_into_d_merge(self, tmp_path: Path) -> None:
        base = tmp_path / "data" / "wiki"
        write_json(
            c_extract_path(base, "countries") / "from_circuits.json",
            [{"text": "Italy", "url": "https://en.wikipedia.org/wiki/Italy"}],
        )
        write_json(
            c_extract_path(base, "countries") / "from_drivers.json",
            ["Italy", "Germany"],
        )

        merge_layer_zero_phase_d(base)

        d_merge_file = d_merge_path(base, "countries") / "countries.json"
        assert d_merge_file.exists()
        result = json.loads(d_merge_file.read_text(encoding="utf-8"))
        assert len(result) == 3

    def test_deduplicates_by_url(self, tmp_path: Path) -> None:
        base = tmp_path / "data" / "wiki"
        italy = {"text": "Italy", "url": "https://en.wikipedia.org/wiki/Italy"}
        write_json(
            c_extract_path(base, "countries") / "a.json",
            [italy],
        )
        write_json(
            c_extract_path(base, "countries") / "b.json",
            [italy, {"text": "France", "url": "https://en.wikipedia.org/wiki/France"}],
        )

        merge_layer_zero_phase_d(base)

        result = json.loads(
            (d_merge_path(base, "countries") / "countries.json").read_text(
                encoding="utf-8",
            ),
        )
        assert len(result) == 2

    def test_deduplicates_strings(self, tmp_path: Path) -> None:
        base = tmp_path / "data" / "wiki"
        write_json(
            c_extract_path(base, "countries") / "from_drivers.json",
            ["Italy", "Germany", "Italy"],
        )

        merge_layer_zero_phase_d(base)

        result = json.loads(
            (d_merge_path(base, "countries") / "countries.json").read_text(
                encoding="utf-8",
            ),
        )
        assert result.count("Italy") == 1

    def test_does_nothing_if_layer_zero_dir_missing(self, tmp_path: Path) -> None:
        merge_layer_zero_phase_d(tmp_path / "nonexistent")

    def test_skips_domain_without_c_extract(self, tmp_path: Path) -> None:
        base = tmp_path / "data" / "wiki"
        (base / "layers" / "0_layer" / "circuits").mkdir(parents=True)

        merge_layer_zero_phase_d(base)

        assert not d_merge_path(base, "circuits").exists()

    def test_produces_d_merge_for_existing_domain_with_single_file(
        self,
        tmp_path: Path,
    ) -> None:
        base = tmp_path / "data" / "wiki"
        payload = [{"text": "Monza", "url": "https://en.wikipedia.org/wiki/Monza"}]
        write_json(c_extract_path(base, "locations") / "from_circuits.json", payload)

        merge_layer_zero_phase_d(base)

        d_merge_file = d_merge_path(base, "locations") / "locations.json"
        assert d_merge_file.exists()
        result = json.loads(d_merge_file.read_text(encoding="utf-8"))
        assert result == payload

    def test_sorts_countries_by_text_for_mixed_strings_and_dicts(
        self,
        tmp_path: Path,
    ) -> None:
        base = tmp_path / "data" / "wiki"
        write_json(
            c_extract_path(base, "countries") / "from_mixed.json",
            [
                {"text": "Poland", "url": "https://example.com/pl"},
                "Argentina",
                {"text": "Brazil", "url": "https://example.com/br"},
            ],
        )

        merge_layer_zero_phase_d(base)

        result = json.loads(
            (d_merge_path(base, "countries") / "countries.json").read_text(
                encoding="utf-8",
            ),
        )
        assert [item if isinstance(item, str) else item["text"] for item in result] == [
            "Argentina",
            "Brazil",
            "Poland",
        ]

    def test_sorts_sponsors_by_text_for_mixed_strings_and_dicts(
        self,
        tmp_path: Path,
    ) -> None:
        base = tmp_path / "data" / "wiki"
        write_json(
            c_extract_path(base, "sponsors") / "from_mixed.json",
            [
                {"text": "Zeta", "url": "https://example.com/z"},
                "Alpha",
                {"text": "Beta"},
            ],
        )

        merge_layer_zero_phase_d(base)

        result = json.loads(
            (d_merge_path(base, "sponsors") / "sponsors.json").read_text(
                encoding="utf-8",
            ),
        )
        assert [item if isinstance(item, str) else item["text"] for item in result] == [
            "Alpha",
            "Beta",
            "Zeta",
        ]
