from scrapers.base.table.columns.types import EnumMarksColumn
from scrapers.base.table.columns.types import MultiColumn
from scrapers.base.table.columns.types import UrlColumn


class EngineManufacturerNameStatusColumn(MultiColumn):
    def __init__(self) -> None:
        super().__init__(
            {
                "manufacturer": UrlColumn(),
                "manufacturer_status": EnumMarksColumn(
                    {"~": "current"},
                    default="former",
                ),
            },
        )
