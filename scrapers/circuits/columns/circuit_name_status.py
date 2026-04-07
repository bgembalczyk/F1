from scrapers.base.table.columns.types.enum_marks import EnumMarksMixin
from scrapers.base.table.columns.types.name_status import NameStatusColumn


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
