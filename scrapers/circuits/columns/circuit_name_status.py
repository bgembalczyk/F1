from scrapers.base.table.columns.types import EnumMarksColumn
from scrapers.base.table.columns.types import MultiColumn
from scrapers.base.table.columns.types import UrlColumn


class CircuitNameStatusColumn(MultiColumn):
    def __init__(self) -> None:
        super().__init__(
            {
                "circuit": UrlColumn(),
                "circuit_status": EnumMarksColumn(
                    {"*": "current", "†": "future"},
                    default="former",
                ),
            },
        )
