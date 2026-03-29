from scrapers.base.table.columns.types import MultiColumn
from scrapers.base.table.columns.types.constructor_part import ConstructorPartColumn


class ConstructorSplitColumn(MultiColumn):
    def __init__(self) -> None:
        super().__init__(
            {
                "chassis_constructor": ConstructorPartColumn(0),
                "engine_constructor": ConstructorPartColumn(1),
            },
        )
