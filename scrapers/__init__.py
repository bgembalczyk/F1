"""Public API for scraper orchestration and domain entrypoints."""

from __future__ import annotations


def __getattr__(name: str):
    if name == "run_wiki_flow":
        from scrapers.wiki.flow_entrypoint import run_wiki_flow

        return run_wiki_flow
    msg = f"module {__name__!r} has no attribute {name!r}"
    raise AttributeError(msg)


__all__ = ["run_wiki_flow"]
