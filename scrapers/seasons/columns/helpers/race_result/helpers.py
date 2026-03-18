from dataclasses import dataclass
from typing import Any
from typing import Protocol

from scrapers.seasons.columns.helpers.constants import CLASSIFIED_DNF_BACKGROUNDS
from scrapers.seasons.columns.helpers.constants import CLASSIFIED_DNF_MARK
from scrapers.seasons.columns.helpers.constants import CLASSIFIED_DNF_NOTE
from scrapers.seasons.columns.helpers.constants import CLASSIFIED_DNF_START_YEAR
from scrapers.seasons.columns.helpers.constants import DOUBLE_POINTS_SEASON_YEAR
from scrapers.seasons.columns.helpers.constants import F2_INELIGIBLE_YEARS
from scrapers.seasons.columns.helpers.constants import FATAL_NOTES_START_YEAR
from scrapers.seasons.columns.helpers.constants import SHARED_DRIVE_NO_POINTS_END_YEAR
from scrapers.seasons.columns.helpers.constants import SHARED_DRIVE_NO_POINTS_START_YEAR
from scrapers.seasons.columns.helpers.constants import SHARED_DRIVE_POINTS_END_YEAR
from scrapers.seasons.columns.helpers.constants import SHARED_DRIVE_POINTS_START_YEAR






def append_note(result: dict[str, Any], note: str) -> None:
    notes = result.setdefault("notes", [])
    if note not in notes:
        notes.append(note)




















