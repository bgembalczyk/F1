import json
from pathlib import Path

from scripts.migrate_data_layout import migrate


def test_migrate_data_layout_maps_legacy_files(tmp_path: Path) -> None:
    base_dir = tmp_path / "data"
    legacy_source = base_dir / "wiki" / "drivers" / "f1_drivers.json"
    legacy_source.parent.mkdir(parents=True, exist_ok=True)
    legacy_source.write_text(json.dumps([{"driver": "A"}]), encoding="utf-8")

    report = migrate(base_dir=base_dir, copy=True)

    new_path = base_dir / "raw" / "drivers" / "list" / "f1_drivers.json"
    assert new_path.exists()
    assert report.migrated == 1
    assert report.missing >= 1


def test_migrate_data_layout_reports_missing(tmp_path: Path) -> None:
    report = migrate(base_dir=tmp_path / "data", copy=True)

    assert report.migrated == 0
    assert report.missing > 0
