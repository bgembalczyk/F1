from scrapers.base.table.columns.types.enum_marks import EnumMarksMixin
from scrapers.base.table.columns.types.name_status import NameStatusColumn


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