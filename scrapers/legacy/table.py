import warnings

from scrapers.core import table as core_table

warnings.warn(
    "scrapers.legacy.table is deprecated; use scrapers.core.table",
    DeprecationWarning,
    stacklevel=2,
)

__all__ = ["core_table"]
