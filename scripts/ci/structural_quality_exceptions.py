from __future__ import annotations

# Auto-curated exceptions for intentional wrappers and transitional APIs.
REDUNDANT_ALIAS_EXCEPTIONS: set[tuple[str, str]] = {
    ("config/app_config_provider.py", "get_http_config"),
    ("infrastructure/cache/file_ttl_cache.py", "serialize"),
    ("models/records/factories/build.py", "build"),
    ("models/records/factories/build.py", "build_record"),
    ("scrapers/base/errors.py", "behavior"),
    ("scrapers/base/factory/record_factory.py", "create"),
    ("scrapers/base/helpers/normalize.py", "normalize_auto_value"),
    ("scrapers/base/helpers/parsing.py", "parse_float_from_text"),
    ("scrapers/base/helpers/parsing.py", "parse_int_from_text"),
    ("scrapers/base/helpers/parsing.py", "parse_number_with_unit"),
    ("scrapers/base/helpers/text.py", "strip_marks"),
    ("scrapers/base/infobox/dsl.py", "from_schema"),
    ("scrapers/base/infobox/service.py", "normalize_result"),
    ("scrapers/base/normalization_pipeline.py", "is_link_list"),
    ("scrapers/base/run_profiles.py", "resolve_cli_profile"),
    ("scrapers/base/table/columns/types/column_factory.py", "FloatColumn"),
    ("scrapers/base/table/columns/types/column_factory.py", "IntColumn"),
    ("scrapers/base/table/headers.py", "normalize_header"),
    ("scrapers/base/table/scraper.py", "parse_row"),
    ("scrapers/deprecation_catalog.py", "get_deprecated_module_migrations"),
    ("scrapers/drivers/infobox/service.py", "build_parser"),
    ("validation/pipeline.py", "validate"),
    ("validation/record_factory_validator.py", "validate_record"),
}

MAX_FUNCTION_LINES_EXCEPTIONS: dict[tuple[str, str], int] = {}
