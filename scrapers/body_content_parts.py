from dataclasses import dataclass

from bs4 import Tag


@dataclass(frozen=True)
class BodyContentParts:
    catlinks: Tag | None
    content_text: Tag | None

