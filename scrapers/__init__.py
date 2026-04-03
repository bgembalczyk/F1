"""Public API for scraper orchestration and domain entrypoints.

Import from this package (or dedicated domain packages) instead of deep module paths.
"""

from scrapers.wiki.flow_entrypoint import run_wiki_flow

__all__ = ["run_wiki_flow"]
