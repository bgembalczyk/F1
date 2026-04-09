from scrapers.columns.types.constructor.part import ConstructorPartColumn
from scrapers.columns.types.multi.multi import MultiColumn


class ConstructorSplitColumn(MultiColumn):
    def __init__(self) -> None:
        super().__init__(
            {
                "chassis_constructor": ConstructorPartColumn(0),
                "engine_constructor": ConstructorPartColumn(1),
            },
        )
