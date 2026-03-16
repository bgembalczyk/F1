from pathlib import Path

from scrapers.data_paths import DataPaths


def test_resolve_legacy_wiki_prefers_new_raw_layout(tmp_path: Path) -> None:
    paths = DataPaths(
        data_root=tmp_path / "data",
        raw_root=tmp_path / "data" / "raw",
        normalized_root=tmp_path / "data" / "normalized",
        checkpoints_root=tmp_path / "data" / "checkpoints",
        legacy_wiki_root=tmp_path / "data" / "wiki",
    )

    new_file = paths.raw_root / "drivers" / "f1_drivers.json"
    legacy_file = paths.legacy_wiki_root / "drivers" / "f1_drivers.json"
    new_file.parent.mkdir(parents=True, exist_ok=True)
    legacy_file.parent.mkdir(parents=True, exist_ok=True)
    new_file.write_text("[]", encoding="utf-8")
    legacy_file.write_text("[1]", encoding="utf-8")

    resolved = paths.resolve_legacy_wiki_read("data/wiki/drivers/f1_drivers.json")

    assert resolved == new_file


def test_resolve_legacy_wiki_falls_back_to_legacy(tmp_path: Path) -> None:
    paths = DataPaths(
        data_root=tmp_path / "data",
        raw_root=tmp_path / "data" / "raw",
        normalized_root=tmp_path / "data" / "normalized",
        checkpoints_root=tmp_path / "data" / "checkpoints",
        legacy_wiki_root=tmp_path / "data" / "wiki",
    )

    legacy_file = paths.legacy_wiki_root / "drivers" / "f1_drivers.json"
    legacy_file.parent.mkdir(parents=True, exist_ok=True)
    legacy_file.write_text("[]", encoding="utf-8")

    resolved = paths.resolve_legacy_wiki_read("data/wiki/drivers/f1_drivers.json")

    assert resolved == legacy_file
