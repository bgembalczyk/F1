from dataclasses import dataclass

from bs4 import Tag


@dataclass(slots=True)
class SectionMatch:
    heading: Tag
    strategy: str
    score: float
