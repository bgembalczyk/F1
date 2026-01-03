from scrapers.base.table.columns.types.constructor_part import ConstructorPartColumn
from scrapers.base.table.columns.types.multi import MultiColumn


class ConstructorSplitColumn(MultiColumn):
    def __init__(self) -> None:
        super().__init__(
            {
                "chassis_constructor": ConstructorPartColumn(0),
                "engine_constructor": ConstructorPartColumn(1),
            }
        )
