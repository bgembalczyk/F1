from models.section_id import SectionId


def section_id_to_label(section_id: SectionId | str) -> str:
    resolved = SectionId.from_raw(section_id).to_export()
    return " ".join(
        resolved.replace("_", " ").replace("-", " ").replace("/", " / ").split(),
    )
