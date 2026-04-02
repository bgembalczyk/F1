from scrapers.base.table.columns.types import EnumMarksMixin
from scrapers.base.table.columns.types import NameStatusColumn


class RaceTitleStatusColumn(NameStatusColumn):
    def __init__(self) -> None:
        super().__init__(
            entity_key="race_title",
            status_extractors={
                "race_status": EnumMarksMixin(
                    {"*": "active"},
                    default="past",
                ),
            },
        )
