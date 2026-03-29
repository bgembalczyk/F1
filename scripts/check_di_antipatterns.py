#!/usr/bin/env python3
from scripts.ci.check_di_antipatterns import *  # noqa: F403
from scripts.ci.check_di_antipatterns import main

if __name__ == "__main__":
    raise SystemExit(main(__import__("sys").argv[1:]))
