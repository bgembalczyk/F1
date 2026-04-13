"""Backward-compatibility shim: IndianapolisOnlyMixin logic is now in IndianapolisOnlyListScraper."""

from scrapers.list.indianapolis_only.base import IndianapolisOnlyListScraper

#: Backward-compat alias.
IndianapolisOnlyMixin = IndianapolisOnlyListScraper

__all__ = ["IndianapolisOnlyMixin"]
