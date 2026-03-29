#!/usr/bin/env python3
from __future__ import annotations

from scripts.ci.check_di_antipatterns import main
from scripts.ci.check_di_antipatterns import run_check
from scripts.ci.check_di_antipatterns import run_check_messages

__all__ = ["main", "run_check", "run_check_messages"]

if __name__ == "__main__":
    raise SystemExit(main(__import__("sys").argv[1:]))
