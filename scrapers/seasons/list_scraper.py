"""DEPRECATED ENTRYPOINT: use scrapers.seasons.entrypoint.run_list_scraper."""

from models.records.factories.build import RECORD_BUILDERS
from scrapers.base.table.builders import build_columns
from scrapers.base.table.builders import build_scraper_config
from scrapers.base.table.columns.types.int import IntColumn
from scrapers.base.table.columns.types.links_list import LinksListColumn
from scrapers.base.table.columns.types.url import UrlColumn
from scrapers.base.table.dsl.column import column
from scrapers.base.table.scraper import F1TableScraper


class SeasonsListScraper(F1TableScraper):
    COMPONENT_METADATA = {
        "domain": "seasons",
        "seed_name": "seasons",
        "layer": "layer_one",
        "output_category": "seasons",
        "component_type": "list_scraper",
        "default_output_path": "raw/seasons/seeds/complete_seasons",
        "legacy_output_path": "seasons/complete_seasons",
    }

    """
    Scraper listy sezonów z:
    https://en.wikipedia.org/wiki/List_of_Formula_One_seasons
    (główna tabela World Championship seasons)
    """

    schema_columns = build_columns(
        column("Season", "season", UrlColumn()),
        column("Races", "races", IntColumn()),
        column("Countries", "countries", IntColumn()),
        column("First", "first", UrlColumn()),
        column("Last", "last", UrlColumn()),
        column("Drivers' Champion (team)", "drivers_champion_team", LinksListColumn()),
        column("Constructors' Champion", "constructors_champion", LinksListColumn()),
        column("Winners", "winners", IntColumn()),
    )

    CONFIG = build_scraper_config(
        url="https://en.wikipedia.org/wiki/List_of_Formula_One_seasons",
        # jeśli id sekcji się kiedyś zmieni - poprawiasz tylko to
        section_id="Seasons",
        # nagłówki, które MUSZĄ wystąpić w tabeli
        expected_headers=[
            "Season",
            "Races",
        ],
        columns=schema_columns,
        record_factory=RECORD_BUILDERS.season_summary,
    )


if __name__ == "__main__":
    from scrapers.cli import run_legacy_wrapper

    run_legacy_wrapper("scrapers.seasons.list_scraper")
