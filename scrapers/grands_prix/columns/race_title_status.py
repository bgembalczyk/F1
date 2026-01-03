from scrapers.base.table.columns.types.enum_marks import EnumMarksColumn
from scrapers.base.table.columns.types.multi import MultiColumn
from scrapers.base.table.columns.types.url import UrlColumn


class RaceTitleStatusColumn(MultiColumn):
    def __init__(self) -> None:
        super().__init__(
            {
                "race_title": UrlColumn(),
                "race_status": EnumMarksColumn(
                    {"*": "active"},
                    default="past",
                ),
            }
        )
