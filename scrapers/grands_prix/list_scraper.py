from pathlib import Path

from scrapers.base.helpers.runner import run_and_export
from scrapers.base.options import ScraperOptions
from scrapers.base.records import record_from_mapping
from scrapers.base.runner import RunConfig
from scrapers.base.table.columns.types.int import IntColumn
from scrapers.base.table.columns.types.links_list import LinksListColumn
from scrapers.base.table.columns.types.seasons import SeasonsColumn
from scrapers.base.table.config import ScraperConfig
from scrapers.base.table.scraper import F1TableScraper
from scrapers.grands_prix.columns.race_title_status import RaceTitleStatusColumn
from scrapers.grands_prix.validation import GrandsPrixRecordValidator


class GrandsPrixListScraper(F1TableScraper):
    """
    Uproszczony scraper np. dla tabeli 'By race title'
    z:
    https://en.wikipedia.org/wiki/List_of_Formula_One_Grands_Prix
    """

    default_validator = GrandsPrixRecordValidator()

    CONFIG = ScraperConfig(
        url="https://en.wikipedia.org/wiki/List_of_Formula_One_Grands_Prix",
        section_id="By_race_title",
        # podzbiór nagłówków – do znalezienia właściwej tabeli
        expected_headers=[
            "Race title",
            "Years held",
        ],
        # mapowanie nagłówek -> klucz w dict
        column_map={
            "Race title": "race_title",
            "Country": "country",
            "Years held": "years_held",
            "Circuits": "circuits",
            "Total": "total",
        },
        # klucz/nagłówek -> kolumna
        #
        # - race_title: MultiColumn → { race_title (link), race_status (enum po znaku *) }
        # - years_held: sezony
        # - races_held: int
        # - country: lista linków [{text, url}, ...]
        columns={
            # Race title → MultiColumn:
            #   - race_title: pierwszy link (UrlColumn) z automatycznym czyszczeniem * / † z .text
            #   - race_status: EnumMarksColumn patrzący na raw_text (gwiazdka = aktywne)
            "race_title": RaceTitleStatusColumn(),
            # Country → lista linków [{text, url}, ...] z czyszczeniem znaczników
            "country": LinksListColumn(),
            # Years held → sezony (lista zakresów/lat)
            "years_held": SeasonsColumn(),
            "circuits": IntColumn(),
            "total": IntColumn(),
        },
        record_factory=record_from_mapping,
    )

    def __init__(
        self,
        *,
        options: ScraperOptions | None = None,
        config: ScraperConfig | None = None,
    ) -> None:
        options = options or ScraperOptions()
        options.validation_mode = "soft"
        super().__init__(options=options, config=config)


if __name__ == "__main__":
    run_and_export(
        GrandsPrixListScraper,
        "grands_prix/f1_grands_prix_by_title.json",
        "grands_prix/f1_grands_prix_by_title.csv",
        run_config=RunConfig(
            output_dir=Path("../../data/wiki"),
            include_urls=True,
        ),
    )
