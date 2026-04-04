from __future__ import annotations

# Auto-curated exceptions for intentional wrappers and transitional APIs.
REDUNDANT_ALIAS_EXCEPTIONS: set[tuple[str, str]] = {
    ("scrapers/base/table/columns/types/column_factory.py", "FloatColumn"),
    ("scrapers/base/table/columns/types/column_factory.py", "IntColumn"),
}

MAX_FUNCTION_LINES_EXCEPTIONS: dict[tuple[str, str], int] = {}
