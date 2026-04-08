from __future__ import annotations

# Auto-curated exceptions for intentional wrappers and transitional APIs.
REDUNDANT_ALIAS_EXCEPTIONS: set[tuple[str, str]] = {
    ("scrapers/base/table/columns/types/column_factory.py", "FloatColumn"),
    ("scrapers/base/table/columns/types/column_factory.py", "IntColumn"),
    ("infrastructure/gemini/cache_service.py", "get"),
    ("infrastructure/gemini/cache_service.py", "set"),
    ("scripts/ci/adr_enforcement_policy.py", "has_adr_reference"),
    ("validation/schema_engine.py", "extract_missing_key"),
}

MAX_FUNCTION_LINES_EXCEPTIONS: dict[tuple[str, str], int] = {}
