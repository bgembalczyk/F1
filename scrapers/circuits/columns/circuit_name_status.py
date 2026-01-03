from scrapers.base.table.columns.types.enum_marks import EnumMarksColumn
from scrapers.base.table.columns.types.multi import MultiColumn
from scrapers.base.table.columns.types.url import UrlColumn


class CircuitNameStatusColumn(MultiColumn):
    def __init__(self) -> None:
        super().__init__(
            {
                "circuit": UrlColumn(),
                "circuit_status": EnumMarksColumn(
                    {"*": "current", "†": "future"},
                    default="former",
                ),
            }
        )
