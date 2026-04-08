#!/usr/bin/env python3
"""Detect forbidden domain term variants and suggest canonical terminology."""

from __future__ import annotations

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from scripts.lib.bootstrap import ensure_repo_root_on_sys_path

REPO_ROOT = ensure_repo_root_on_sys_path()

from scripts.lib.check_runner import run_cli  # noqa: E402
from scripts.lib.domain_terminology import GLOSSARY_PATH  # noqa: E402
from scripts.lib.domain_terminology import parse_forbidden_term_map  # noqa: E402

SOURCE_DIRS: tuple[str, ...] = (
    "models",
    "layers",
    "validation",
    "infrastructure",
    "complete_extractor",
)

EXCLUDE_PATH_PARTS: tuple[str, ...] = ("__pycache__",)

ALLOWED_FORBIDDEN_USAGE_PATHS: set[Path] = {
    Path("models/mappers/field_aliases.py"),
    Path("models/records/factories/build.py"),
}


def token_pattern(term: str) -> re.Pattern[str]:
    return re.compile(rf"(?<![a-zA-Z0-9_]){re.escape(term)}(?![a-zA-Z0-9_])")


def run_check() -> list[str]:
    glossary = REPO_ROOT / GLOSSARY_PATH
    if not glossary.exists():
        return [f"missing glossary file: {GLOSSARY_PATH}"]

    forbidden_map = parse_forbidden_term_map(glossary)
    if not forbidden_map:
        return [f"no forbidden terms configured in: {GLOSSARY_PATH}"]

    patterns = {term: token_pattern(term) for term in forbidden_map}
    errors: list[str] = []

    for source_dir in SOURCE_DIRS:
        root = REPO_ROOT / source_dir
        if not root.exists():
            continue

        for py_file in root.rglob("*.py"):
            if any(part in EXCLUDE_PATH_PARTS for part in py_file.parts):
                continue

            rel_path = py_file.relative_to(REPO_ROOT)
            if rel_path in ALLOWED_FORBIDDEN_USAGE_PATHS:
                continue

            content = py_file.read_text(encoding="utf-8")
            for forbidden, canonical in forbidden_map.items():
                if patterns[forbidden].search(content):
                    errors.append(
                        f"forbidden term '{forbidden}' in {rel_path} "
                        f"(use '{canonical}')",
                    )

    return errors


def main(argv: list[str] | None = None) -> int:
    del argv
    return run_cli("domain-terminology", run_check)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
