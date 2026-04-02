from scrapers.base.helpers.transformers import append_transformer
from scrapers.base.options import ScraperOptions
from scrapers.base.table.config import ScraperConfig
from scrapers.base.transformers.points_scoring_systems_history import (
    PointsScoringSystemsHistoryTransformer,
)
from scrapers.points.base_points_scraper import BasePointsScraper
from scrapers.points.config_factory import POINTS_SCORING_SYSTEMS_HISTORY_COLUMNS
from scrapers.points.config_factory import POINTS_SCORING_SYSTEMS_HISTORY_CONFIG


class PointsScoringSystemsHistoryScraper(BasePointsScraper):
    """
    Tabela: List of Formula One World Championship points scoring systems
    used throughout history.
    https://en.wikipedia.org/wiki/List_of_Formula_One_World_Championship_points_scoring_systems
    """

    schema_columns = POINTS_SCORING_SYSTEMS_HISTORY_COLUMNS
    CONFIG = POINTS_SCORING_SYSTEMS_HISTORY_CONFIG

    def __init__(
        self,
        *,
        options: ScraperOptions | None = None,
        config: ScraperConfig | None = None,
    ) -> None:
        transformer = PointsScoringSystemsHistoryTransformer()
        super().__init__(
            options=append_transformer(options, transformer),
            config=config,
        )


if __name__ == "__main__":
    from scrapers.base.deprecated_entrypoint import run_deprecated_entrypoint

    run_deprecated_entrypoint()
