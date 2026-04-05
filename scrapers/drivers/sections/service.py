from __future__ import annotations

from models.value_objects import SectionId
from scrapers.base.sections.adapter import SectionAdapterEntry
from scrapers.base.sections.service import BaseSectionExtractionService
from scrapers.drivers.sections.common import BaseDriverResultsSectionParser
from scrapers.drivers.sections.constants import SECTION_CONFIGS
from scrapers.drivers.sections.results import DriverResultsSectionParser
from scrapers.wiki.parsers.sections.helpers import profile_entry_aliases
from scrapers.wiki.parsers.sections.normalization import normalize_section_text


class DriverSectionExtractionService(BaseSectionExtractionService):
    domain = "drivers"
    flatten_records = True

    _CANONICAL_SECTION_ID_BY_NORMALIZED = {
        normalize_section_text(config.section_id): config.section_id
        for config, _aliases in SECTION_CONFIGS
    }

    def build_entries(self) -> list[SectionAdapterEntry]:
        raw_parser = DriverResultsSectionParser(
            options=self.require_options(),
            url=self.require_url(),
        )
        return [
            SectionAdapterEntry(
                section_id=config.section_id,
                aliases=profile_entry_aliases(
                    self.domain,
                    config.section_id,
                    *aliases,
                ),
                parser=BaseDriverResultsSectionParser.from_config(
                    parser=raw_parser,
                    config=config,
                ),
            )
            for config, aliases in SECTION_CONFIGS
        ]

    def _build_record_metadata(
        self,
        *,
        section,
        section_metadata,
    ) -> dict[str, str | dict[str, object]]:
        metadata = dict(
            super()._build_record_metadata(
                section=section,
                section_metadata=section_metadata,
            ),
        )
        canonical_section_id = self._CANONICAL_SECTION_ID_BY_NORMALIZED.get(
            normalize_section_text(str(section.section_id)),
            str(section.section_id),
        )
        canonical_section_id = SectionId.from_raw(canonical_section_id).to_export()
        metadata["section_id"] = canonical_section_id
        section_meta = dict(metadata["section_metadata"])
        section_meta["section_id"] = canonical_section_id
        metadata["section_metadata"] = section_meta
        return metadata
