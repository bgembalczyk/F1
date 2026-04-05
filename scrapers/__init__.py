"""Public API for scraper orchestration and domain entrypoints."""

from __future__ import annotations

from typing import Any

__all__ = ["run_wiki_flow"]


def run_wiki_flow(*args: Any, **kwargs: Any) -> Any:
    """Compatibility wrapper avoiding circular imports during package init."""

    from scrapers.wiki.flow_entrypoint import run_wiki_flow as _run_wiki_flow

    return _run_wiki_flow(*args, **kwargs)
