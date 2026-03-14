from pathlib import Path

from models.records.factories import build_season_summary_record
from scrapers.base.helpers.runner import run_and_export
from scrapers.base.run_config import RunConfig
from scrapers.base.table.columns.types.int import IntColumn
from scrapers.base.table.columns.types.links_list import LinksListColumn
from scrapers.base.table.columns.types.url import UrlColumn
from scrapers.base.table.config import ScraperConfig
from scrapers.base.table.dsl.column import column
from scrapers.base.table.dsl.table_schema import TableSchemaDSL
from scrapers.base.table.scraper import F1TableScraper


class SeasonsListScraper(F1TableScraper):
    """
    Scraper listy sezonów z:
    https://en.wikipedia.org/wiki/List_of_Formula_One_seasons
    (główna tabela World Championship seasons)
    """

    schema_columns = [
        column("Season", "season", UrlColumn()),
        column("Races", "races", IntColumn()),
        column("Countries", "countries", IntColumn()),
        column("First", "first", UrlColumn()),
        column("Last", "last", UrlColumn()),
        column("Drivers' Champion (team)", "drivers_champion_team", LinksListColumn()),
        column("Constructors' Champion", "constructors_champion", LinksListColumn()),
        column("Winners", "winners", IntColumn()),
    ]

    CONFIG = ScraperConfig(
        url="https://en.wikipedia.org/wiki/List_of_Formula_One_seasons",
        # jeśli id sekcji się kiedyś zmieni - poprawiasz tylko to
        section_id="Seasons",
        # nagłówki, które MUSZĄ wystąpić w tabeli
        expected_headers=[
            "Season",
            "Races",
        ],
        schema=TableSchemaDSL(columns=schema_columns),
        record_factory=build_season_summary_record,
    )


if __name__ == "__main__":
    run_and_export(
        SeasonsListScraper,
        "seasons/f1_seasons.json",
        "seasons/f1_seasons.csv",
        run_config=RunConfig(
            output_dir=Path("../../data/wiki"),
            include_urls=True,
        ),
    )
