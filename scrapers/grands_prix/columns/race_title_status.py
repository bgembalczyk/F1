from scrapers.base.table.columns.types import EnumMarksColumn
from scrapers.base.table.columns.types import MultiColumn
from scrapers.base.table.columns.types import UrlColumn


class RaceTitleStatusColumn(MultiColumn):
    def __init__(self) -> None:
        super().__init__(
            {
                "race_title": UrlColumn(),
                "race_status": EnumMarksColumn(
                    {"*": "active"},
                    default="past",
                ),
            },
        )
