"""DEPRECATED shim for `scrapers/grands_prix_list_scraper.py`.

Remove this module after 2026-12-31. Import from `scrapers.grands_prix_list_scraper` instead.
"""

from __future__ import annotations

import warnings

warnings.warn(
    "Module `scrapers.list_scraper_grands_prix` is deprecated and will be removed after 2026-12-31; use `scrapers.grands_prix_list_scraper`.",
    DeprecationWarning,
    stacklevel=2,
)

from scrapers.grands_prix_list_scraper import *  # noqa: F401,F403
