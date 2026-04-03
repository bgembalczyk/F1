from __future__ import annotations

from layers.composition import create_default_wiki_pipeline_application
from layers.path_resolver import DEFAULT_PATH_RESOLVER


def run_wiki_flow() -> None:
    """Run the canonical wiki flow with the default full scenario."""
    application = create_default_wiki_pipeline_application(
        base_wiki_dir=DEFAULT_PATH_RESOLVER.exports_root.resolve(),
        base_debug_dir=DEFAULT_PATH_RESOLVER.debug_root.resolve(),
    )
    application.run_full()
