from __future__ import annotations

import argparse
import sys
from pathlib import Path

from scripts.ci.git_diff import run_git_and_capture_stdout
from scripts.ci.reporting import split_csv

CONVENTION_PREFIXES = (
    "drivers",
    "constructors",
    "circuits",
    "seasons",
    "grands_prix",
)
CONVENTION_SUFFIXES = (
    "_list_scraper",
    "_detail_scraper",
    "_pipeline_service",
)


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Block newly added scraper modules that violate canonical naming "
            "(<domain>_list_scraper.py, <domain>_detail_scraper.py, "
            "<domain>_pipeline_service.py)."
        ),
    )
    parser.add_argument("--base-sha", required=True)
    parser.add_argument("--head-sha", required=True)
    parser.add_argument("--changed-files", default="")
    return parser.parse_args(argv)


def list_added_files(base_sha: str, head_sha: str) -> list[str]:
    result = run_git_and_capture_stdout(
        ["diff", "--name-status", "--diff-filter=A", base_sha, head_sha],
    )
    if result.returncode != 0:
        return []

    added_files: list[str] = []
    for line in result.stdout.splitlines():
        parts = line.split("\t", maxsplit=1)
        if len(parts) != 2:
            continue
        status, file_path = parts
        if status.strip() == "A":
            added_files.append(file_path.strip())
    return added_files


def is_target_module(file_path: str) -> bool:
    return file_path.startswith("scrapers/") and file_path.endswith(".py")


def has_domain_prefix(stem: str) -> bool:
    return any(stem.startswith(f"{prefix}_") for prefix in CONVENTION_PREFIXES)


def is_convention_compliant(stem: str) -> bool:
    return any(stem.endswith(suffix) for suffix in CONVENTION_SUFFIXES)


def find_violations(added_files: list[str]) -> list[str]:
    violations: list[str] = []
    for file_path in sorted(added_files):
        if not is_target_module(file_path):
            continue
        stem = Path(file_path).stem
        if not has_domain_prefix(stem):
            continue
        if is_convention_compliant(stem):
            continue
        violations.append(file_path)
    return violations


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    changed_files = [p for p in split_csv(args.changed_files) if p]

    added_files = list_added_files(args.base_sha, args.head_sha)
    if changed_files:
        changed_set = set(changed_files)
        added_files = [path for path in added_files if path in changed_set]

    if not added_files:
        print("No new files added in diff scope; scraper module naming gate skipped.")
        return 0

    violations = find_violations(added_files)
    if not violations:
        print("New scraper modules comply with naming convention: OK")
        return 0

    print("::error::Detected new scraper modules that violate naming convention:")
    for violation in violations:
        print(f" - {violation}")
    print(
        "Expected one of: <domain>_list_scraper.py, <domain>_detail_scraper.py, "
        "<domain>_pipeline_service.py.",
    )
    return 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
