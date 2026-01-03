from scrapers.base.table.columns.types.multi import MultiColumn
from scrapers.base.table.columns.types.regex import RegexColumn


class LastLengthUsedColumn(MultiColumn):
    def __init__(self) -> None:
        super().__init__(
            {
                "last_length_used_km": RegexColumn(
                    r"([\d\.,]+)\s*km",
                    cast=float,
                    normalize_number=True,
                ),
                "last_length_used_mi": RegexColumn(
                    r"\(([\d\.,]+)\s*mi\)",
                    cast=float,
                    normalize_number=True,
                ),
            }
        )
