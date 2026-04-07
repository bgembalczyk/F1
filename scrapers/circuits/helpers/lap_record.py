import re
from typing import Any

from bs4 import Tag

from models.services.helpers import split_delimited_text
from scrapers.base.helpers.tables.header import is_repeated_header_row
from scrapers.base.helpers.tables.lap_records import LapRecordsTableScraper
from scrapers.base.helpers.text import clean_wiki_text
from scrapers.base.helpers.time import parse_time_seconds_from_text
from scrapers.circuits.helpers.constants import DETAILS_MIN_SCORE_WITHOUT_COMMA
from scrapers.circuits.helpers.constants import DETAILS_PARTS_BONUS_2
from scrapers.circuits.helpers.constants import DETAILS_PARTS_BONUS_3
from scrapers.circuits.helpers.constants import DETAILS_PARTS_BONUS_4
from scrapers.circuits.helpers.constants import DETAILS_PARTS_COUNT_FEW
from scrapers.circuits.helpers.constants import DETAILS_PARTS_COUNT_MANY
from scrapers.circuits.helpers.constants import DETAILS_PARTS_COUNT_MEDIUM
from scrapers.circuits.helpers.layout import layout_from_spanning_header
from scrapers.circuits.helpers.logger import logger
from scrapers.circuits.models.services.lap_record_merging import normalize_lap_record


def extract_time(text: str) -> float | None:
    if not text:
        return None

    head = text.split("(", 1)[0].strip()
    time_match = re.match(r"^\s*(\d+:\d{2}(?:\.\d+)?)\b", head)
    time_str = time_match.group(1) if time_match else None

    sec = parse_time_seconds_from_text(time_str) if time_str else None

    if sec is None:
        m = re.search(r"\b(\d+:\d{2}(?:\.\d+)?)\b", text)
        if m:
            sec = parse_time_seconds_from_text(m.group(1))

    return sec


def is_speed_paren(s: str) -> bool:
    """Sprawdza czy tekst zawiera jednostki prędkości (km/h, mph)."""
    s_low = s.lower()
    return ("km/h" in s_low) or ("mph" in s_low)


def score_details_candidate(s: str) -> int:
    """Ocenia czy dany tekst jest dobrym kandydatem na szczegóły lap record'u."""
    if not s:
        return -10
    if is_speed_paren(s):
        return -100

    parts = split_delimited_text(s, pattern=r",")
    score = 0

    if len(parts) >= DETAILS_PARTS_COUNT_MANY:
        score += DETAILS_PARTS_BONUS_4
    elif len(parts) == DETAILS_PARTS_COUNT_MEDIUM:
        score += DETAILS_PARTS_BONUS_3
    elif len(parts) == DETAILS_PARTS_COUNT_FEW:
        score += DETAILS_PARTS_BONUS_2
    else:
        score -= 2

    if any(re.fullmatch(r"\d{4}", p) for p in parts):
        score += 5

    if "," not in s and score < DETAILS_MIN_SCORE_WITHOUT_COMMA:
        score -= 3

    return score


def select_details_paren(text: str) -> list[str]:
    parens = re.findall(r"\(([^)]*)\)", text or "")
    if not parens:
        return []

    best = max(parens, key=score_details_candidate)
    if score_details_candidate(best) <= 0:
        return []

    return split_delimited_text(best, pattern=r",")


def is_lap_record_table(
    headers: list[str],
    lap_scraper: LapRecordsTableScraper,
) -> bool:
    if lap_scraper.headers_match(headers):
        return True

    header_set = set(headers)
    return "Time" in header_set and (
        "Driver" in header_set or "Driver/Rider" in header_set
    )


def collect_lap_records(
    table: Tag,
    headers: list[str],
    base_layout: str | None,
    lap_scraper: LapRecordsTableScraper,
) -> list[dict[str, Any]]:
    all_records: list[dict[str, Any]] = []
    current_layout = base_layout

    for tr in table.find_all("tr")[1:]:
        cells = tr.find_all(["th", "td"])
        if not cells or all(not c.get_text(strip=True) for c in cells):
            continue

        layout = layout_from_spanning_header(cells, headers)
        if layout:
            current_layout = layout
            continue

        cleaned_cells = [clean_wiki_text(c.get_text(strip=True)) for c in cells]
        if is_repeated_header_row(cleaned_cells, headers):
            logger.debug("Pomijam powtórzony wiersz nagłówka w tabeli rekordów.")
            continue

        row_records = lap_scraper.parse_multi_row(tr, cells, headers)
        if not row_records:
            continue

        layout_name = current_layout or base_layout
        for record in row_records:
            if not record:
                continue
            normalize_lap_record(record)
            if layout_name:
                record.setdefault("layout", layout_name)
            all_records.append(record)

    return all_records
