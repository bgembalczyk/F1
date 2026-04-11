from collections.abc import Iterable
from dataclasses import dataclass

from scrapers.infobox.schemas.field import InfoboxSchemaField


@dataclass(frozen=True)
class InfoboxFieldSpec:
    key: str
    labels: Iterable[str]
    parser: str | None = None

    def build(self) -> InfoboxSchemaField:
        return InfoboxSchemaField(
            key=self.key,
            labels=tuple(self.labels),
            parser=self.parser,
        )
