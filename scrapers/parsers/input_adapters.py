"""Compatibility shim for parser-level imports."""

from scrapers.input_adapters import as_dict_fragment
from scrapers.input_adapters import as_soup
from scrapers.input_adapters import as_table_fragments
from scrapers.input_adapters import as_tag

__all__ = [
    "as_dict_fragment",
    "as_soup",
    "as_table_fragments",
    "as_tag",
]
