from scrapers.base.table.builders import build_metric_columns
from scrapers.base.table.builders import metric_column
from scrapers.constructors.config_factory import build_constructor_list_config
from scrapers.constructors.base_constructor_list_scraper import (
    BaseConstructorListScraper,
)
from scrapers.constructors.constants import CONSTRUCTOR_FASTEST_LAPS_HEADER
from scrapers.constructors.constants import CONSTRUCTOR_PODIUMS_HEADER
from scrapers.constructors.constants import CONSTRUCTOR_POINTS_HEADER
from scrapers.constructors.constants import CONSTRUCTOR_POLES_HEADER
from scrapers.constructors.constants import CONSTRUCTOR_RACES_ENTERED_HEADER
from scrapers.constructors.constants import CONSTRUCTOR_RACES_STARTED_HEADER
from scrapers.constructors.constants import CONSTRUCTOR_SEASONS_HEADER
from scrapers.constructors.constants import CONSTRUCTOR_WINS_HEADER
from scrapers.constructors.constants import FORMER_CONSTRUCTORS_EXPECTED_HEADERS
from scrapers.constructors.sections.list_section import FormerConstructorsSectionParser


class FormerConstructorsListScraper(BaseConstructorListScraper):
    """
    Byli konstruktorzy - sekcja 'Former constructors'
    z:
    https://en.wikipedia.org/wiki/List_of_Formula_One_constructors
    """

    schema_columns = BaseConstructorListScraper.build_schema_columns(
        BaseConstructorListScraper.build_common_metadata_columns(),
        [BaseConstructorListScraper.build_licensed_in_column()],
        build_metric_columns(
            [
                metric_column(CONSTRUCTOR_SEASONS_HEADER, "seasons", "seasons"),
                metric_column(
                    CONSTRUCTOR_RACES_ENTERED_HEADER,
                    "races_entered",
                    "races_entered",
                ),
                metric_column(
                    CONSTRUCTOR_RACES_STARTED_HEADER,
                    "races_started",
                    "races_started",
                ),
                metric_column(CONSTRUCTOR_WINS_HEADER, "wins", "wins"),
                metric_column(CONSTRUCTOR_POINTS_HEADER, "points", "points"),
                metric_column(CONSTRUCTOR_POLES_HEADER, "poles", "poles"),
                metric_column(
                    CONSTRUCTOR_FASTEST_LAPS_HEADER,
                    "fastest_laps",
                    "fastest_laps",
                ),
                metric_column(CONSTRUCTOR_PODIUMS_HEADER, "podiums", "podiums"),
            ],
        ),
    )

    CONFIG = build_constructor_list_config(
        section_id="Former_constructors",
        expected_headers=FORMER_CONSTRUCTORS_EXPECTED_HEADERS,
        columns=schema_columns,
    )

    section_label = "Former constructors"
    section_parser_class = FormerConstructorsSectionParser
