from __future__ import annotations

import argparse
import json
import shutil
import sys
from dataclasses import asdict
from dataclasses import dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scrapers.data_paths import default_data_paths


@dataclass(frozen=True)
class MigrationEntry:
    source: str
    destination: str
    status: str


@dataclass(frozen=True)
class MigrationReport:
    migrated: list[MigrationEntry]
    missing: list[MigrationEntry]

    def to_dict(self) -> dict[str, object]:
        return {
            "migrated": [asdict(entry) for entry in self.migrated],
            "missing": [asdict(entry) for entry in self.missing],
        }


def map_legacy_wiki_path(relative_path: Path, *, repo_root: Path) -> Path:
    parts = relative_path.parts
    data_root = repo_root / "data"
    if any(part.startswith("complete_") for part in parts):
        return data_root / "normalized" / relative_path
    return data_root / "raw" / relative_path


def build_migration_report(*, data_root: Path, apply_changes: bool) -> MigrationReport:
    paths = default_data_paths()
    legacy_root = data_root / paths.legacy_wiki_root

    migrated: list[MigrationEntry] = []
    missing: list[MigrationEntry] = []

    if not legacy_root.exists():
        return MigrationReport(migrated=[], missing=[])

    for source in sorted(legacy_root.rglob("*")):
        if source.is_dir():
            continue

        rel = source.relative_to(legacy_root)
        destination = map_legacy_wiki_path(rel, repo_root=data_root)

        if not source.exists():
            missing.append(
                MigrationEntry(
                    source=str(source),
                    destination=str(destination),
                    status="missing_source",
                ),
            )
            continue

        if apply_changes:
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, destination)

        migrated.append(
            MigrationEntry(
                source=str(source),
                destination=str(destination),
                status="copied" if apply_changes else "planned",
            ),
        )

    return MigrationReport(migrated=migrated, missing=missing)


def main() -> None:
    parser = argparse.ArgumentParser(description="Migrate data/wiki layout to domain layout.")
    parser.add_argument("--data-root", type=Path, default=Path("."), help="Repository root.")
    parser.add_argument("--apply", action="store_true", help="Copy files to new layout.")
    parser.add_argument(
        "--report",
        type=Path,
        default=Path("data/checkpoints/migration/wiki_to_domain_layout_report.json"),
        help="Path to migration report JSON.",
    )

    args = parser.parse_args()
    report = build_migration_report(data_root=args.data_root, apply_changes=args.apply)

    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(
        json.dumps(report.to_dict(), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    print(
        "[migration] finished "
        f"migrated={len(report.migrated)} missing={len(report.missing)} "
        f"report={args.report}",
    )


if __name__ == "__main__":
    main()
