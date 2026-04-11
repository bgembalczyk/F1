from scrapers.columns.types.mixins.enum import EnumMarksMixin
from scrapers.columns.types.multi.name_status_column.base import NameStatusColumn


class CircuitNameStatusColumn(NameStatusColumn):
    def __init__(self) -> None:
        super().__init__(
            entity_key="circuit",
            status_extractors={
                "circuit_status": EnumMarksMixin(
                    {"*": "current", "†": "future"},
                    default="former",
                ),
            },
        )


__all__ = ["CircuitNameStatusColumn"]