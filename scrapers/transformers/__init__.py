from scrapers.base.transformers.drivers_championships import (
    DriversChampionshipsTransformer,
)
from scrapers.base.transformers.failed_to_make_restart import (
    FailedToMakeRestartTransformer,
)
from scrapers.base.transformers.fatalities_car import FatalitiesCarTransformer
from scrapers.base.transformers.helpers import apply_transformers
from scrapers.base.transformers.normalize_links import NormalizeLinksTransformer
from scrapers.base.transformers.pipeline import TransformersPipeline
from scrapers.base.transformers.points_scoring_systems_history import (
    PointsScoringSystemsHistoryTransformer,
)
from scrapers.base.transformers.record_factory import RecordFactoryTransformer
from scrapers.base.transformers.record_transformer import RecordTransformer
from scrapers.base.transformers.shortened_race_points import (
    ShortenedRacePointsTransformer,
)

__all__ = [
    "DriversChampionshipsTransformer",
    "FailedToMakeRestartTransformer",
    "FatalitiesCarTransformer",
    "apply_transformers",
    "NormalizeLinksTransformer",
    "TransformersPipeline",
    "PointsScoringSystemsHistoryTransformer",
    "RecordFactoryTransformer",
    "RecordTransformer",
    "ShortenedRacePointsTransformer",
]
