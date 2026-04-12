from dataclasses import dataclass


@dataclass(frozen=True)
class ExtractedCategoryLink:
    text: str
    href: str
