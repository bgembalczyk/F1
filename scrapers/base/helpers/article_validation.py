"""Backward-compatible aliases for section validation helpers.

Nowa, wspólna logika walidacji sekcji jest utrzymywana w
`scrapers.base.helpers.sections`.
"""

from scrapers.base.helpers.sections import get_category_texts
from scrapers.base.helpers.sections import has_category_keyword
from scrapers.base.helpers.sections import has_navbox_template_link

__all__ = [
    "get_category_texts",
    "has_category_keyword",
    "has_navbox_template_link",
]
