"""Central defaults shared across CLI, executors and service wiring."""

from __future__ import annotations

from pathlib import Path
from typing import Final

DEFAULT_WIKI_OUTPUT_DIR: Final[Path] = Path("../../data/wiki")
DEFAULT_DEBUG_DIR: Final[Path] = Path("../../data/debug")

DEFAULT_INCLUDE_URLS: Final[bool] = True
DEFAULT_QUALITY_REPORT: Final[bool] = False
DEFAULT_ERROR_REPORT: Final[bool] = False
DEFAULT_VERBOSE: Final[bool] = False
DEFAULT_TRACE: Final[bool] = False

DEFAULT_LEGACY_CLI_PROFILE: Final[str] = "list_scraper"
