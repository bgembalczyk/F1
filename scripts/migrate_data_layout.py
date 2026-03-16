#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import shutil
from dataclasses import asdict
from dataclasses import dataclass
from pathlib import Path

from scrapers.config import DataPaths
from scrapers.config import default_data_paths
from scrapers.wiki.seed_registry import WIKI_LIST_JOB_REGISTRY


@dataclass(frozen=True)
class MigrationItem:
    source: str
    destination: str
    status: str


@dataclass(frozen=True)
class MigrationReport:
    base_dir: str
    migrated: int
    missing: int
    skipped_existing: int
    items: list[MigrationItem]


def _build_mappings(paths: DataPaths) -> list[tuple[Path, Path]]:
    mappings: list[tuple[Path, Path]] = []
    for entry in WIKI_LIST_JOB_REGISTRY:
        source = paths.legacy_wiki / entry.legacy_json_output_path
        destination = paths.base_dir / entry.json_output_path
        mappings.append((source, destination))

    checkpoint_files = (
        "step_0_layer0_drivers.json",
        "step_1_layer1_drivers.json",
        "step_registry.json",
        "step_audit.json",
        "step_audit.csv",
    )
    for filename in checkpoint_files:
        mappings.append((paths.legacy_wiki / "checkpoints" / filename, paths.checkpoint_file(filename)))
    return mappings


def migrate(*, base_dir: Path, copy: bool = False, overwrite: bool = False) -> MigrationReport:
    paths = default_data_paths(base_dir=base_dir)
    items: list[MigrationItem] = []
    migrated = 0
    missing = 0
    skipped_existing = 0

    for source, destination in _build_mappings(paths):
        if not source.exists():
            missing += 1
            items.append(MigrationItem(str(source), str(destination), "missing"))
            continue

        if destination.exists() and not overwrite:
            skipped_existing += 1
            items.append(MigrationItem(str(source), str(destination), "skipped_existing"))
            continue

        destination.parent.mkdir(parents=True, exist_ok=True)
        if copy:
            shutil.copy2(source, destination)
            action = "copied"
        else:
            destination.write_bytes(source.read_bytes())
            action = "moved"
            if source != destination:
                source.unlink()
        migrated += 1
        items.append(MigrationItem(str(source), str(destination), action))

    return MigrationReport(
        base_dir=str(base_dir),
        migrated=migrated,
        missing=missing,
        skipped_existing=skipped_existing,
        items=items,
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Migrate data/wiki layout to data/raw + data/checkpoints.")
    parser.add_argument("--base-dir", default="data", help="Base data dir (default: data).")
    parser.add_argument("--copy", action="store_true", help="Copy files instead of moving them.")
    parser.add_argument("--overwrite", action="store_true", help="Overwrite destination files if they already exist.")
    parser.add_argument("--report", default=None, help="Optional path to JSON report output.")
    args = parser.parse_args()

    report = migrate(base_dir=Path(args.base_dir), copy=args.copy, overwrite=args.overwrite)

    payload = {
        "base_dir": report.base_dir,
        "migrated": report.migrated,
        "missing": report.missing,
        "skipped_existing": report.skipped_existing,
        "items": [asdict(item) for item in report.items],
    }

    if args.report:
        report_path = Path(args.report)
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
