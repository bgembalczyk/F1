from collections.abc import Mapping
from typing import Any
from typing import cast

from models.records.base_factory import BaseRecordFactory
from models.records.season_summary import SeasonSummaryRecord


class SeasonSummaryRecordFactory(BaseRecordFactory):
    def build(self, record: Mapping[str, Any]) -> SeasonSummaryRecord:
        payload = self.apply_spec(
            record,
            {
                "list_field_normalizers": {
                    "link": ["season", "first", "last"],
                    "int": ["races", "countries", "winners"],
                    "link_list": ["drivers_champion_team", "constructors_champion"],
                },
                "defaults": {
                    "drivers_champion_team": [],
                    "constructors_champion": [],
                },
            },
        )
        return cast("SeasonSummaryRecord", payload)
