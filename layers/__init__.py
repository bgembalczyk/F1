"""Public API for the wiki pipeline layer package.

Canonical entrypoint for external integrations:
- ``create_default_wiki_pipeline_facade``
- ``create_default_wiki_pipeline_application`` (compatibility wrapper)

All other modules under ``layers`` should be treated as internal wiring.
"""

from layers.application import create_default_wiki_pipeline_application
from layers.application import create_default_wiki_pipeline_facade
from layers.composition import create_default_wiki_pipeline_application

__all__ = [
    "create_default_wiki_pipeline_application",
    "create_default_wiki_pipeline_facade",
]
