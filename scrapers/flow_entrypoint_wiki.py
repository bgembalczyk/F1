from __future__ import annotations

from path_resolver.base import DEFAULT_PATH_RESOLVER


def run_wiki_flow() -> None:
    from wiki_pipeline.create_default.applications import create_default_wiki_pipeline_application

    application = create_default_wiki_pipeline_application(
        base_wiki_dir=DEFAULT_PATH_RESOLVER.exports_root.resolve(),
        base_debug_dir=DEFAULT_PATH_RESOLVER.debug_root.resolve(),
    )
    application.run_full()
