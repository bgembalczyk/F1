from scrapers.base.table.columns.types import EnumMarksMixin
from scrapers.base.table.columns.types import NameStatusColumn


class EngineManufacturerNameStatusColumn(NameStatusColumn):
    def __init__(self) -> None:
        super().__init__(
            entity_key="manufacturer",
            status_extractors={
                "manufacturer_status": EnumMarksMixin(
                    {"~": "current"},
                    default="former",
                ),
            },
        )
