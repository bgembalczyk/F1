from path_resolver.base import DEFAULT_PATH_RESOLVER
from wiki_pipeline.create_default.applications import create_default_wiki_pipeline_application

if __name__ == "__main__":
    application = create_default_wiki_pipeline_application(
        base_wiki_dir=DEFAULT_PATH_RESOLVER.exports_root.resolve(),
        base_debug_dir=DEFAULT_PATH_RESOLVER.debug_root.resolve(),
    )
    application.run_full()
