from models.records.factories.build import build_constructor_record
from scrapers.base.table.builders import build_columns
from scrapers.base.table.builders import build_metric_columns
from scrapers.base.table.builders import build_scraper_config
from scrapers.base.table.builders import metric_column
from scrapers.base.table.dsl.column import column
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
from scrapers.constructors.sections.list_section import ConstructorsListSectionParser


class FormerConstructorsListScraper(BaseConstructorListScraper):
    """
    Byli konstruktorzy - sekcja 'Former constructors'
    z:
    https://en.wikipedia.org/wiki/List_of_Formula_One_constructors
    """

    schema_columns = build_columns(
        BaseConstructorListScraper.build_common_metadata_columns(),
        BaseConstructorListScraper.build_licensed_in_column(),
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

    CONFIG = build_scraper_config(
        url="https://en.wikipedia.org/wiki/List_of_Formula_One_constructors",
        section_id="Former_constructors",
        expected_headers=FORMER_CONSTRUCTORS_EXPECTED_HEADERS,
        columns=schema_columns,
        record_factory=build_constructor_record,
    )

    section_label = "Former constructors"
    section_parser_class = ConstructorsListSectionParser


if __name__ == "__main__":
    from scrapers.cli import run_legacy_wrapper

    run_legacy_wrapper("scrapers.constructors.former_constructors_list")
