from pathlib import Path

from scripts.migrate_data_layout import build_migration_report
from scripts.migrate_data_layout import map_legacy_wiki_path


def test_map_legacy_wiki_path_routes_complete_to_normalized(tmp_path: Path) -> None:
    destination = map_legacy_wiki_path(
        Path("drivers/complete_drivers/A.json"),
        repo_root=tmp_path,
    )

    assert destination == tmp_path / "data" / "normalized" / "drivers" / "complete_drivers" / "A.json"


def test_build_migration_report_copies_to_new_layout(tmp_path: Path) -> None:
    legacy_file = tmp_path / "data" / "wiki" / "drivers" / "f1_drivers.json"
    legacy_file.parent.mkdir(parents=True, exist_ok=True)
    legacy_file.write_text("[]", encoding="utf-8")

    report = build_migration_report(data_root=tmp_path, apply_changes=True)

    assert len(report.migrated) == 1
    assert report.migrated[0].status == "copied"
    migrated_file = tmp_path / "data" / "raw" / "drivers" / "f1_drivers.json"
    assert migrated_file.exists()
    assert report.missing == []
