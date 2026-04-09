from dataclasses import dataclass
from typing import Sequence

from scrapers.infobox.schemas.schema import ParserType


@dataclass(frozen=True)
class InfoboxSchemaField:
    key: str
    labels: Sequence[str]
    parser: ParserType | None = None
