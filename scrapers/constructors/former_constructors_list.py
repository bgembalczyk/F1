from scrapers.base.table.builders import MetricColumnSpec
from scrapers.base.table.builders import build_metric_columns
from scrapers.constructors.base_constructor_list_scraper import (
    BaseConstructorListScraper,
)
from scrapers.constructors.config_factory import build_constructor_list_config
from scrapers.constructors.constants import CONSTRUCTOR_FASTEST_LAPS_HEADER
from scrapers.constructors.constants import CONSTRUCTOR_PODIUMS_HEADER
from scrapers.constructors.constants import CONSTRUCTOR_POINTS_HEADER
from scrapers.constructors.constants import CONSTRUCTOR_POLES_HEADER
from scrapers.constructors.constants import CONSTRUCTOR_RACES_ENTERED_HEADER
from scrapers.constructors.constants import CONSTRUCTOR_RACES_STARTED_HEADER
from scrapers.constructors.constants import CONSTRUCTOR_SEASONS_HEADER
from scrapers.constructors.constants import CONSTRUCTOR_WINS_HEADER
from scrapers.constructors.constants import CONSTRUCTORS_FORMER_EXPECTED_HEADERS
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
                MetricColumnSpec(CONSTRUCTOR_SEASONS_HEADER, "seasons", "seasons"),
                MetricColumnSpec(
                    CONSTRUCTOR_RACES_ENTERED_HEADER,
                    "races_entered",
                    "races_entered",
                ),
                MetricColumnSpec(
                    CONSTRUCTOR_RACES_STARTED_HEADER,
                    "races_started",
                    "races_started",
                ),
                MetricColumnSpec(CONSTRUCTOR_WINS_HEADER, "wins", "wins"),
                MetricColumnSpec(CONSTRUCTOR_POINTS_HEADER, "points", "points"),
                MetricColumnSpec(CONSTRUCTOR_POLES_HEADER, "poles", "poles"),
                MetricColumnSpec(
                    CONSTRUCTOR_FASTEST_LAPS_HEADER,
                    "fastest_laps",
                    "fastest_laps",
                ),
                MetricColumnSpec(CONSTRUCTOR_PODIUMS_HEADER, "podiums", "podiums"),
            ],
        ),
    )

    CONFIG = build_constructor_list_config(
        section_id="Former_constructors",
        expected_headers=CONSTRUCTORS_FORMER_EXPECTED_HEADERS,
        columns=schema_columns,
    )

    section_label = "Former constructors"
    section_parser_class = FormerConstructorsSectionParser
