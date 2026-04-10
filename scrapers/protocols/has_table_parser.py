from __future__ import annotations

import warnings

from scrapers.contracts.protocols.has_table_parser import HasTableParser

warnings.warn(
    "scrapers.protocols.has_table_parser is deprecated and will be removed after the transition period; "
    "use scrapers.contracts.protocols.has_table_parser instead.",
    DeprecationWarning,
    stacklevel=2,
)

__all__ = ["HasTableParser"]
