from collections.abc import Mapping
from typing import Any
from typing import cast

from models.mappers.field_aliases import FIELD_ALIASES
from models.records.base_factory import BaseRecordFactory
from models.records.constructor import ConstructorRecord
from models.records.factories.helpers import (
    normalize_optional_link_list_or_link_or_string,
)


class ConstructorRecordFactory(BaseRecordFactory):
    def build(self, record: Mapping[str, Any]) -> ConstructorRecord:
        payload = self.apply_aliases(
            record,
            FIELD_ALIASES["constructor"],
            "constructor",
        )
        self.normalize_link_fields(payload, ["constructor"])
        self.normalize_link_list_fields(
            payload,
            ["engine", "based_in", "antecedent_teams"],
        )
        self.normalize_seasons_fields(payload, ["seasons"])

        payload["licensed_in"] = normalize_optional_link_list_or_link_or_string(
            self.normalizer,
            payload.get("licensed_in"),
            "licensed_in",
        )

        self.normalize_int_fields(
            payload,
            [
                "races_entered",
                "races_started",
                "drivers",
                "total_entries",
                "wins",
                "points",
                "poles",
                "fastest_laps",
                "podiums",
                "wcc_titles",
                "wdc_titles",
            ],
        )
        self.set_defaults(
            payload,
            {
                "engine": [],
                "based_in": [],
                "seasons": [],
                "antecedent_teams": [],
            },
        )
        return cast("ConstructorRecord", payload)
