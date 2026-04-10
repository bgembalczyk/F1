"""DEPRECATED shim for `scrapers/drivers_list_scraper.py`.

Remove this module after 2026-12-31. Import from `scrapers.drivers_list_scraper` instead.
"""

from __future__ import annotations

import warnings

warnings.warn(
    "Module `scrapers.list_scraper_drivers` is deprecated and will be removed after 2026-12-31; use `scrapers.drivers_list_scraper`.",
    DeprecationWarning,
    stacklevel=2,
)

from scrapers.drivers_list_scraper import *  # noqa: F401,F403
