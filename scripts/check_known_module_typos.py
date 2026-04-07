#!/usr/bin/env python3
"""Static check for known module/file typos in key packages."""

from __future__ import annotations

import sys
from pathlib import Path

if str(Path(__file__).resolve().parents[1]) not in sys.path:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from scripts.lib.bootstrap import ensure_repo_root_on_sys_path

REPO_ROOT = ensure_repo_root_on_sys_path()

from scripts.lib.check_runner import run_cli  # noqa: E402
from scripts.lib.known_typos import run_known_typos_check  # noqa: E402


def main(argv: list[str] | None = None) -> int:
    del argv
    return run_cli(
        "known-module-typos",
        lambda: run_known_typos_check(REPO_ROOT),
    )


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
