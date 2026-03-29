from __future__ import annotations

import argparse
import re
from pathlib import PurePosixPath

from scripts.ci.git_diff import collect_commit_messages
from scripts.ci.git_diff import get_unified_diff
from scripts.ci.git_diff import list_changed_files

ARCHITECTURE_PREFIXES: tuple[str, ...] = (
    "layers/",
    "scrapers/base/",
    "tests/architecture/",
)
ADR_PATTERN = re.compile(r"\bADR-\d{4}\b", re.IGNORECASE)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Wymaga referencji ADR-XXXX, gdy PR/commit zmienia ścieżki "
            "architektoniczne i zmiana nie jest wyłącznie kosmetyczna."
        )
    )
    parser.add_argument("--base-sha", required=True)
    parser.add_argument("--head-sha", required=True)
    parser.add_argument("--pr-title", default="")
    parser.add_argument("--pr-body", default="")
    return parser.parse_args()


def is_architecture_path(path: str) -> bool:
    normalized = PurePosixPath(path).as_posix()
    return any(normalized.startswith(prefix) for prefix in ARCHITECTURE_PREFIXES)


def is_cosmetic_line(content: str) -> bool:
    stripped = content.strip()
    if not stripped:
        return True
    if stripped.startswith("#"):
        return True
    return False


def has_non_cosmetic_changes(base_sha: str, head_sha: str, files: list[str]) -> bool:
    if not files:
        return False

    diff_result = get_unified_diff(base_sha, head_sha, files)
    if diff_result.returncode != 0:
        return True

    if not diff_result.stdout.strip():
        return False

    for line in diff_result.stdout.splitlines():
        if line.startswith(("+++", "---", "@@")):
            continue
        if not line.startswith(("+", "-")):
            continue

        marker = line[:1]
        payload = line[1:]
        if marker in {"+", "-"} and not is_cosmetic_line(payload):
            return True

    return False


def main() -> int:
    args = parse_args()

    changed_files = list_changed_files(args.base_sha, args.head_sha)
    architecture_files = [path for path in changed_files if is_architecture_path(path)]

    if not architecture_files:
        print("Brak zmian w ścieżkach architektonicznych; gate ADR pominięty.")
        return 0

    if not has_non_cosmetic_changes(args.base_sha, args.head_sha, architecture_files):
        print(
            "Wykryto wyłącznie zmiany kosmetyczne (formatowanie/komentarze) "
            "w ścieżkach architektonicznych; gate ADR pominięty."
        )
        return 0

    combined_text = "\n".join(
        [
            args.pr_title,
            args.pr_body,
            collect_commit_messages(args.base_sha, args.head_sha),
        ]
    )

    if ADR_PATTERN.search(combined_text):
        print("Referencja ADR-XXXX znaleziona. Gate ADR zaliczony.")
        return 0

    print("::error::Zmiany architektoniczne wymagają referencji ADR-XXXX w PR lub commit message.")
    print(f"::error::Dotknięte ścieżki: {', '.join(architecture_files)}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
