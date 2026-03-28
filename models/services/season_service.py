from datetime import datetime
from datetime import timezone

from models.domain_utils.years import extract_years
from models.records.constants import WIKI_SEASON_URL
from models.value_objects.season_ref import SeasonRef


def parse_seasons(
    text: str,
    *,
    current_year: int | None = None,
) -> list[SeasonRef]:
    """
    Zamienia tekst w stylu:
        '1973, 1975-1982, 1984' lub '2014-present'
    na listę jawnych obiektów SeasonRef.

    'present' (case-insensitive) -> aktualny rok.
    """
    if not text:
        return []

    if current_year is None:
        current_year = datetime.now(timezone.utc).year

    years = extract_years(text, current_year=current_year)
    return [
        SeasonRef(year=year, url=WIKI_SEASON_URL.format(year=year)) for year in years
    ]
