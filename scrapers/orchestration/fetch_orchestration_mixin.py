"""Backward-compatibility shim: FetchOrchestrationMixin logic is now in WikiScraper."""

from scrapers.scraper_wiki import WikiScraper

#: Backward-compat alias — FetchOrchestrationMixin is effectively WikiScraper now.
FetchOrchestrationMixin = WikiScraper

__all__ = ["FetchOrchestrationMixin"]
