"""Public API for the wiki pipeline layer package.

Canonical entrypoint for external integrations:
- ``create_default_wiki_pipeline_facade``
- ``create_default_wiki_pipeline_application`` (compatibility wrapper)

All other modules under ``layers`` should be treated as internal wiring.
"""

from __future__ import annotations

import layers.application as _application


def create_default_wiki_pipeline_application(*args, **kwargs):
    """Create the default wiki pipeline application lazily."""

    return _application.create_default_wiki_pipeline_application(*args, **kwargs)


def create_default_wiki_pipeline_facade(*args, **kwargs):
    """Create the default wiki pipeline facade lazily."""

    return _application.create_default_wiki_pipeline_facade(*args, **kwargs)


__all__ = [
    "create_default_wiki_pipeline_application",
    "create_default_wiki_pipeline_facade",
]
