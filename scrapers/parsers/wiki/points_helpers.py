from __future__ import annotations

import re
from typing import Any

from models.services.season import parse_seasons
from scrapers.constants_points import HISTORICAL_POSITIONS
from scrapers.constants_points import POINTS_NOTES_HEADER
from scrapers.constants_points import POINTS_SCORING_HISTORY_EXPECTED_HEADERS
from scrapers.constants_points import ROLE_PATTERN
from scrapers.constants_points import SHORTENED_RACE_EXPECTED_HEADERS
from scrapers.constants_points import SPRINT_POSITIONS
from scrapers.constants_points import SPRINT_QUALIFYING_EXPECTED_HEADERS
from scrapers.helpers.parsing import parse_int_from_text
from scrapers.parsers.wiki.table.base import WikiTableBaseMapper

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


