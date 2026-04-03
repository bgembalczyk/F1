"""Public API for scraper orchestration and domain entrypoints."""

from __future__ import annotations


def __getattr__(name: str):
    if name == "run_wiki_flow":
        from scrapers.wiki.flow_entrypoint import run_wiki_flow

        return run_wiki_flow
    msg = f"module {__name__!r} has no attribute {name!r}"
    raise AttributeError(msg)


from __future__ import annotations


def run_wiki_flow() -> None:
    """Run the canonical wiki flow entrypoint.

    Import lazily to avoid circular imports during package initialization
    (``layers`` imports many ``scrapers`` submodules).
    """

    from scrapers.wiki.flow_entrypoint import run_wiki_flow as _run_wiki_flow

    _run_wiki_flow()


__all__ = ["run_wiki_flow"]
