from __future__ import annotations

import warnings

from scrapers.contracts.protocols.data_frame_formatter import DataFrameFormatterProtocol

warnings.warn(
    "scrapers.protocols.data_frame_formatter is deprecated and will be removed after the transition period; "
    "use scrapers.contracts.protocols.data_frame_formatter instead.",
    DeprecationWarning,
    stacklevel=2,
)

__all__ = ["DataFrameFormatterProtocol"]
