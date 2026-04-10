from __future__ import annotations

import warnings

from scrapers.contracts.protocols.fieldnames_strategy import FieldnamesStrategyProtocol

warnings.warn(
    "scrapers.protocols.fieldnames_strategy is deprecated and will be removed after the transition period; "
    "use scrapers.contracts.protocols.fieldnames_strategy instead.",
    DeprecationWarning,
    stacklevel=2,
)

__all__ = ["FieldnamesStrategyProtocol"]
