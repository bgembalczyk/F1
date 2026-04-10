from dataclasses import dataclass


@dataclass(frozen=True)
class SectionResolution:
    section_id: str
    candidates: tuple[str, ...]
    matched_candidate: str | None
    heading_match: object | None
