from scrapers.base.options import ScraperOptions


def append_transformer(
    options: ScraperOptions | None,
    transformer: object,
) -> ScraperOptions:
    resolved = options or ScraperOptions()
    resolved.transformers = [
        *list(resolved.transformers or []),
        transformer,
    ]
    return resolved
