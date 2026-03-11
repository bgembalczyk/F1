from scrapers.base.table.columns.types.enum_marks import EnumMarksColumn
from scrapers.base.table.columns.types.multi import MultiColumn
from scrapers.base.table.columns.types.url import UrlColumn


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
