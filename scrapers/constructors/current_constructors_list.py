"""DEPRECATED ENTRYPOINT: use scrapers.constructors.entrypoint.run_list_scraper."""

from models.records.factories.build import RECORD_BUILDERS
from scrapers.base.table.builders import build_columns
from scrapers.base.table.builders import build_scraper_config
from scrapers.base.table.columns.types.auto import AutoColumn
from scrapers.base.table.columns.types.links_list import LinksListColumn
from scrapers.base.table.dsl.column import column
from scrapers.constructors.base_constructor_list_scraper import (
    BaseConstructorListScraper,
)
from scrapers.constructors.constants import CONSTRUCTOR_ANTECEDENT_TEAMS_HEADER
from scrapers.constructors.constants import CONSTRUCTOR_BASED_IN_HEADER
from scrapers.constructors.constants import CONSTRUCTOR_DRIVERS_HEADER
from scrapers.constructors.constants import CONSTRUCTOR_ENGINE_HEADER
from scrapers.constructors.constants import CONSTRUCTOR_LICENSED_IN_HEADER
from scrapers.constructors.constants import CURRENT_CONSTRUCTORS_EXPECTED_HEADERS
from scrapers.constructors.constants import CURRENT_YEAR
from scrapers.constructors.sections.list_section import ConstructorsListSectionParser
from scrapers.wiki.component_metadata import ComponentMetadata


class CurrentConstructorsListScraper(BaseConstructorListScraper):
    COMPONENT_METADATA = ComponentMetadata.build_layer_one_list_scraper(
        domain="constructors",
        default_output_path="raw/constructors/seeds/complete_constructors",
        legacy_output_path="constructors/complete_constructors",
    )

    """
    Aktualni konstruktorzy - sekcja
    'Constructors for the current season' z:
    https://en.wikipedia.org/wiki/List_of_Formula_One_constructors
    """

    schema_columns = build_columns(
        column(CONSTRUCTOR_ENGINE_HEADER, "engine", LinksListColumn()),
        column(CONSTRUCTOR_LICENSED_IN_HEADER, "licensed_in", AutoColumn()),
        column(CONSTRUCTOR_BASED_IN_HEADER, "based_in", LinksListColumn()),
        BaseConstructorListScraper.build_common_stats_columns(),
        column(CONSTRUCTOR_DRIVERS_HEADER, "drivers", AutoColumn()),
        BaseConstructorListScraper.build_common_metadata_columns(),
        column(
            CONSTRUCTOR_ANTECEDENT_TEAMS_HEADER,
            "antecedent_teams",
            LinksListColumn(),
        ),
    )

    CONFIG = build_scraper_config(
        url="https://en.wikipedia.org/wiki/List_of_Formula_One_constructors",
        section_id=f"Constructors_for_the_{CURRENT_YEAR}_season",
        expected_headers=CURRENT_CONSTRUCTORS_EXPECTED_HEADERS,
        columns=schema_columns,
        record_factory=RECORD_BUILDERS.constructor,
    )

    section_label = "Current constructors"
    section_parser_class = ConstructorsListSectionParser


if __name__ == "__main__":
    from scrapers.cli import run_current_legacy_wrapper

    run_current_legacy_wrapper()
