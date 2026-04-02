from scrapers.base.table.columns.types import EnumMarksMixin
from scrapers.base.table.columns.types import NameStatusColumn


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
