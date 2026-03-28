"""Backward-compatible import path for grand prix section helpers."""

from scrapers.grands_prix.helpers.sections import has_grand_prix_category
from scrapers.grands_prix.helpers.sections import has_grand_prix_navbox
from scrapers.grands_prix.helpers.sections import is_grand_prix_article

__all__ = [
    "has_grand_prix_navbox",
    "has_grand_prix_category",
    "is_grand_prix_article",
]
