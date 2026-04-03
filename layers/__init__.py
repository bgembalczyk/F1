"""Public API for the wiki pipeline layer package.

Canonical entrypoint for external integrations:
- ``create_default_wiki_pipeline_facade``
- ``create_default_wiki_pipeline_application`` (compatibility wrapper)

All other modules under ``layers`` should be treated as internal wiring.
"""

from __future__ import annotations

from layers.application import create_default_wiki_pipeline_facade
from layers.composition import create_default_wiki_pipeline_application


def create_default_wiki_pipeline_application(*args, **kwargs):
    """Create the default wiki pipeline application lazily."""

    from layers.application import create_default_wiki_pipeline_application as _factory

    return _factory(*args, **kwargs)


def create_default_wiki_pipeline_facade(*args, **kwargs):
    """Create the default wiki pipeline facade lazily."""

    from layers.application import create_default_wiki_pipeline_facade as _factory

    return _factory(*args, **kwargs)

__all__ = [
    "create_default_wiki_pipeline_application",
    "create_default_wiki_pipeline_facade",
]
