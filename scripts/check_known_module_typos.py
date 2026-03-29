#!/usr/bin/env python3
"""Static check for known module/file typos in key packages."""

from __future__ import annotations

from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

try:
    from scripts.lib.check_runner import run_cli
    from scripts.lib.known_typos import run_known_typos_check
except ModuleNotFoundError:
    from lib.check_runner import run_cli
    from lib.known_typos import run_known_typos_check


def main() -> int:
    return run_cli("known-module-typos", run_known_typos_check)


if __name__ == "__main__":
    raise SystemExit(main())
