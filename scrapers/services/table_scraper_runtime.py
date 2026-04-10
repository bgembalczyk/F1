"""Runtime factory helpers for table scraper infrastructure."""

from __future__ import annotations

from scrapers.base.extractors.table import TableExtractor
from validation.record_factory_validator import adapt_record_factory_validator


def build_table_extractor(
    *,
    config,
    include_urls: bool,
    normalize_empty_values: bool,
    model_fields: set[str] | None,
    debug_dir: str | None,
) -> TableExtractor:
    return TableExtractor(
        config=config,
        include_urls=include_urls,
        normalize_empty_values=normalize_empty_values,
        model_fields=model_fields,
        debug_dir=debug_dir,
    )


def ensure_record_factory_validator(*, validator, record_factory) -> None:
    if validator is None or validator.record_factory_validator is not None:
        return
    validator.set_record_factory_validator(
        adapt_record_factory_validator(record_factory),
    )
