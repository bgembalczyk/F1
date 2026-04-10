from dataclasses import dataclass

SectionTree = dict[str, Any]


@dataclass(slots=True)
class SectionTreeMatch:
    section: SectionTree
    strategy: str
    score: float
