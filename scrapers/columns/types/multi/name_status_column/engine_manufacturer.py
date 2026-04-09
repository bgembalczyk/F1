from scrapers.columns.types.mixins.enum import EnumMarksMixin
from scrapers.columns.types.multi.name_status_column.base import NameStatusColumn


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


__all__ = ["EngineManufacturerNameStatusColumn"]
