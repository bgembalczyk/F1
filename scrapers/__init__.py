"""Public API for scraper orchestration and domain entrypoints.

Import from this package (or dedicated domain packages) instead of deep module paths.
"""

from scrapers.cli import run_wiki_cli

__all__ = ["run_wiki_cli"]
