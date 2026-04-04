"""DEPRECATED ENTRYPOINT: use scrapers.constructors.entrypoint.run_list_scraper."""

from scrapers.base.table.columns.types import AutoColumn
from scrapers.base.table.columns.types import LinksListColumn
from scrapers.base.table.dsl.column import ColumnSpec
from scrapers.constructors.base_constructor_list_scraper import (
    BaseConstructorListScraper,
)
from scrapers.constructors.config_factory import build_constructor_list_config
from scrapers.constructors.constants import CONSTRUCTOR_ANTECEDENT_TEAMS_HEADER
from scrapers.constructors.constants import CONSTRUCTOR_BASED_IN_HEADER
from scrapers.constructors.constants import CONSTRUCTOR_DRIVERS_HEADER
from scrapers.constructors.constants import CONSTRUCTOR_ENGINE_HEADER
from scrapers.constructors.constants import CONSTRUCTOR_LICENSED_IN_HEADER
from scrapers.constructors.constants import CURRENT_CONSTRUCTORS_EXPECTED_HEADERS
from scrapers.constructors.sections.list_section import CurrentConstructorsSectionParser


class CurrentConstructorsListScraper(BaseConstructorListScraper):
    """
    Aktualni konstruktorzy - sekcja
    'Constructors for the current season' z:
    https://en.wikipedia.org/wiki/List_of_Formula_One_constructors
    """

    schema_columns = BaseConstructorListScraper.build_schema_columns(
        [ColumnSpec(CONSTRUCTOR_ENGINE_HEADER, "engine", LinksListColumn())],
        [ColumnSpec(CONSTRUCTOR_LICENSED_IN_HEADER, "licensed_in", AutoColumn())],
        [ColumnSpec(CONSTRUCTOR_BASED_IN_HEADER, "based_in", LinksListColumn())],
        BaseConstructorListScraper.build_common_stats_columns(),
        [ColumnSpec(CONSTRUCTOR_DRIVERS_HEADER, "drivers", AutoColumn())],
        BaseConstructorListScraper.build_common_metadata_columns(),
        [
            ColumnSpec(
                CONSTRUCTOR_ANTECEDENT_TEAMS_HEADER,
                "antecedent_teams",
                LinksListColumn(),
            ),
        ],
    )

    CONFIG = build_constructor_list_config(
        section_id="Constructors_for_the_2026_season",
        expected_headers=CURRENT_CONSTRUCTORS_EXPECTED_HEADERS,
        columns=schema_columns,
    )

    section_label = "Current constructors"
    section_parser_class = CurrentConstructorsSectionParser
