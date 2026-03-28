from models.value_objects import SectionId
from scrapers.base.sections.section_id_resolver import SectionIdResolver


def resolve_section_candidates(
    *,
    domain: str,
    section_id: SectionId | str,
    alternative_section_ids: tuple[str, ...] = (),
) -> tuple[str, ...]:
    """Resolve section candidates in deterministic order."""
    return SectionIdResolver(domain=domain).resolve_candidates(
        section_id=section_id,
        alternative_section_ids=alternative_section_ids,
    )
