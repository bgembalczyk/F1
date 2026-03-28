from models.value_objects import SectionId
from scrapers.base.sections.constants import DOMAIN_CRITICAL_SECTIONS


def section_id_to_label(section_id: SectionId | str) -> str:
    resolved = SectionId.from_raw(section_id).to_export()
    return " ".join(
        resolved.replace("_", " ").replace("-", " ").replace("/", " / ").split(),
    )


def resolve_section_candidates(
    *,
    domain: str,
    section_id: SectionId | str,
    alternative_section_ids: tuple[str, ...] = (),
) -> tuple[str, ...]:
    """Resolve section candidates in deterministic order.

    Order:
    1) canonical section ID,
    2) alternative IDs,
    3) text label fallback derived from canonical ID.
    """
    resolved_section_id = SectionId.from_raw(section_id).to_export()
    resolved_alternatives = alternative_section_ids
    if not resolved_alternatives:
        for candidate in DOMAIN_CRITICAL_SECTIONS.get(domain, ()):  # pragma: no branch
            if SectionId.from_raw(candidate.section_id).to_export() == resolved_section_id:
                resolved_alternatives = candidate.alternative_section_ids
                break

    candidates: list[str] = [resolved_section_id]
    for alias in resolved_alternatives:
        if alias and alias not in candidates:
            candidates.append(alias)

    section_label = section_id_to_label(resolved_section_id)
    if section_label and section_label not in candidates:
        candidates.append(section_label)
    return tuple(candidates)
