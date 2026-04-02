#!/usr/bin/env python3
"""Detect forbidden domain term variants and suggest canonical terminology."""

from __future__ import annotations

import importlib.util
from pathlib import Path
import re
import sys

_BOOTSTRAP_PATH = Path(__file__).resolve().parent / "lib" / "bootstrap.py"
_BOOTSTRAP_SPEC = importlib.util.spec_from_file_location(
    "_scripts_bootstrap",
    _BOOTSTRAP_PATH,
)
assert _BOOTSTRAP_SPEC and _BOOTSTRAP_SPEC.loader
_BOOTSTRAP_MODULE = importlib.util.module_from_spec(_BOOTSTRAP_SPEC)
_BOOTSTRAP_SPEC.loader.exec_module(_BOOTSTRAP_MODULE)

REPO_ROOT = _BOOTSTRAP_MODULE.ensure_repo_root_on_sys_path()

from scripts.lib.check_runner import run_cli
from scripts.lib.domain_terminology import GLOSSARY_PATH
from scripts.lib.domain_terminology import parse_forbidden_term_map

SOURCE_DIRS: tuple[str, ...] = (
    "models",
    "layers",
    "validation",
    "infrastructure",
    "complete_extractor",
)

EXCLUDE_PATH_PARTS: tuple[str, ...] = (
    "__pycache__",
)

ALLOWED_FORBIDDEN_USAGE_PATHS: set[Path] = {
    Path("models/mappers/field_aliases.py"),
    Path("models/records/factories/build.py"),
}


def _token_pattern(term: str) -> re.Pattern[str]:
    return re.compile(rf"(?<![a-zA-Z0-9_]){re.escape(term)}(?![a-zA-Z0-9_])")


def run_check() -> list[str]:
    glossary = REPO_ROOT / GLOSSARY_PATH
    if not glossary.exists():
        return [f"missing glossary file: {GLOSSARY_PATH}"]

    forbidden_map = parse_forbidden_term_map(glossary)
    if not forbidden_map:
        return [f"no forbidden terms configured in: {GLOSSARY_PATH}"]

    patterns = {term: _token_pattern(term) for term in forbidden_map}
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
                        f"forbidden term '{forbidden}' in {rel_path} (use '{canonical}')",
                    )

    return errors


def main(argv: list[str] | None = None) -> int:
    del argv
    return run_cli("domain-terminology", run_check)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
