#!/usr/bin/env python3
"""Static check for known module/file typos in key packages."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

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
from scripts.lib.known_typos import run_known_typos_check


def run_check() -> list[str]:
    return run_known_typos_check(REPO_ROOT)


def main(argv: list[str] | None = None) -> int:
    del argv
    return run_cli("known-module-typos", run_check)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
