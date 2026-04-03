from __future__ import annotations

import argparse
import re
import subprocess
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class TerminologyRule:
    canonical: str
    forbidden: tuple[str, ...]


TERMINOLOGY_RULES: tuple[TerminologyRule, ...] = (
    TerminologyRule(canonical="grand_prix", forbidden=("grandprix", "grand-prix")),
    TerminologyRule(canonical="grands_prix", forbidden=("grandprixes", "grand_prixes")),
    TerminologyRule(canonical="season", forbidden=("championship_year",)),
)

SCANNED_EXTENSIONS = {".py", ".md", ".yml", ".yaml"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Sprawdza spójność terminologiczną i wykrywa zabronione synonimy."
    )
    parser.add_argument("--base-sha", required=True)
    parser.add_argument("--head-sha", required=True)
    return parser.parse_args()


def list_changed_files(base_sha: str, head_sha: str) -> list[Path]:
    proc = subprocess.run(
        ["git", "diff", "--name-only", "--diff-filter=ACMR", base_sha, head_sha],
        check=False,
        capture_output=True,
        text=True,
    )
    if proc.returncode != 0:
        return []

    files: list[Path] = []
    for line in proc.stdout.splitlines():
        rel_path = line.strip()
        if not rel_path:
            continue
        path = Path(rel_path)
        if path.suffix in SCANNED_EXTENSIONS and path.exists():
            files.append(path)
    return files


def scan_text_forbidden_terms(text: str, rules: tuple[TerminologyRule, ...]) -> list[tuple[int, str, str]]:
    issues: list[tuple[int, str, str]] = []
    for line_number, line in enumerate(text.splitlines(), start=1):
        for rule in rules:
            for forbidden in rule.forbidden:
                if re.search(re.escape(forbidden), line, flags=re.IGNORECASE):
                    issues.append((line_number, forbidden, rule.canonical))
    return issues


def scan_files(files: list[Path], rules: tuple[TerminologyRule, ...]) -> list[str]:
    errors: list[str] = []
    for file_path in files:
        try:
            content = file_path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue

        for line_number, forbidden, canonical in scan_text_forbidden_terms(content, rules):
            errors.append(
                f"{file_path}:{line_number}: znaleziono zabroniony termin '{forbidden}' "
                f"(użyj canonical: '{canonical}')"
            )

    return errors


def main() -> int:
    args = parse_args()
    files = list_changed_files(args.base_sha, args.head_sha)

    if not files:
        print("Brak zmienionych plików do sprawdzenia terminologii.")
        return 0

    errors = scan_files(files, TERMINOLOGY_RULES)
    if errors:
        for error in errors:
            print(f"::error::{error}")
        return 1

    print("Spójność terminologiczna: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
