from dataclasses import dataclass
from dataclasses import field

from scrapers.records.assemblers.base import BaseRecordAssemblerInput
from scrapers.records.sections.season import SeasonRecordSections


@dataclass(frozen=True)
class SeasonPayloadDTO:
    sections: SeasonRecordSections
    base: BaseRecordAssemblerInput = field(default_factory=BaseRecordAssemblerInput)
