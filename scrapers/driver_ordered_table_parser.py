import warnings

warnings.warn(
    "scrapers.driver_ordered_table_parser is deprecated; "
    "import from scrapers.parsers.table.base_ordered instead.",
    DeprecationWarning,
    stacklevel=2,
)

from scrapers.parsers.table.base_ordered import DriverOrderedTableParser  # noqa: E402, F401

__all__ = ["DriverOrderedTableParser"]
