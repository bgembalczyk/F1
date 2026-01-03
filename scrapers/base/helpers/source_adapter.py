from infrastructure.http_client.policies.http import HttpPolicy
from scrapers.base.options import ScraperOptions
from scrapers.base.source_adapter import SourceAdapter


def build_source_adapter(
    options: ScraperOptions,
    *,
    policy: HttpPolicy | None = None,
) -> SourceAdapter:
    """Utwórz adapter źródła na podstawie ScraperOptions."""
    return options.with_source_adapter(policy=policy)
