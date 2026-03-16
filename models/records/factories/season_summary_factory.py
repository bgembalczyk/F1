from collections.abc import Mapping
from typing import Any, cast

from models.records.base_factory import BaseRecordFactory
from models.records.season_summary import SeasonSummaryRecord


class SeasonSummaryRecordFactory(BaseRecordFactory):
    def build(self, record: Mapping[str, Any]) -> SeasonSummaryRecord:
        payload = dict(record)
        self.normalize_link_fields(payload, ["season", "first", "last"])
        self.normalize_int_fields(payload, ["races", "countries", "winners"])
        self.normalize_link_list_fields(
            payload,
            ["drivers_champion_team", "constructors_champion"],
        )
        self.set_defaults(
            payload,
            {
                "drivers_champion_team": [],
                "constructors_champion": [],
            },
        )
        return cast("SeasonSummaryRecord", payload)
