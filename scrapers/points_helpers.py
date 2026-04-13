from __future__ import annotations

import re

# Position keys for the points history table (excluding "1st" which is
# handled separately)


def normalize_header(header: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", header.lower())


def normalize_column_name(header: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", header.lower()).strip("_")


def build_expected_header_lookup(expected_headers: list[str]) -> dict[str, str]:
    return {
        normalize_header(header): normalize_column_name(header)
        for header in expected_headers
    }
