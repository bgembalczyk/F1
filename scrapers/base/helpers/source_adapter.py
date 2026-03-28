from infrastructure.http_client.policies.http import HttpPolicy
from scrapers.base.factory.runtime_factory import ScraperRuntimeFactory
from scrapers.base.options import ScraperOptions
from scrapers.base.source_adapter import SourceAdapter


def build_source_adapter(
    options: ScraperOptions,
    *,
    policy: HttpPolicy | None = None,
) -> SourceAdapter:
    """Utwórz adapter źródła na podstawie ScraperOptions."""
    runtime = ScraperRuntimeFactory().build(options=options, policy=policy)
    return runtime.source_adapter
