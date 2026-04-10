from __future__ import annotations

import warnings

from scrapers.contracts.protocols.data_frame_formatter import DataFrameFormatterProtocol
from scrapers.contracts.protocols.fieldnames_strategy import FieldnamesStrategyProtocol
from scrapers.contracts.protocols.has_table_parser import HasTableParser

warnings.warn(
    "scrapers.protocols is deprecated and will be removed after the transition period; "
    "use scrapers.contracts.protocols instead.",
    DeprecationWarning,
    stacklevel=2,
)

__all__ = [
    "DataFrameFormatterProtocol",
    "FieldnamesStrategyProtocol",
    "HasTableParser",
]
