"""DEPRECATED shim for `scrapers/circuits_detail_scraper.py`.

Remove this module after 2026-12-31. Import from `scrapers.circuits_detail_scraper` instead.
"""

from __future__ import annotations

import warnings

warnings.warn(
    "Module `scrapers.circuits_single_scraper` is deprecated and will be removed after 2026-12-31; use `scrapers.circuits_detail_scraper`.",
    DeprecationWarning,
    stacklevel=2,
)

from scrapers.circuits_detail_scraper import *  # noqa: F401,F403
