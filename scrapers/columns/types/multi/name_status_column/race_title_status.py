from scrapers.columns.types.multi.name_status_column.base import NameStatusColumn


class RaceTitleStatusColumn(NameStatusColumn):
    def __init__(self) -> None:
        super().__init__(
            entity_key="race_title",
            status_extractors={
                "race_status": self.enum_status_extractor(
                    {"*": "active"},
                    default="past",
                ),
            },
        )


__all__ = ["RaceTitleStatusColumn"]
