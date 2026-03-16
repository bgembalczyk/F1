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
        payload = self.apply_spec(
            record,
            {
                "aliases": FIELD_ALIASES["constructor"],
                "record_name": "constructor",
                "field_normalizers": {
                    "licensed_in": lambda value,
                    field: normalize_optional_link_list_or_link_or_string(
                        self.normalizer,
                        value,
                        field,
                    ),
                },
                "list_field_normalizers": {
                    "link": ["constructor"],
                    "link_list": ["engine", "based_in", "antecedent_teams"],
                    "seasons": ["seasons"],
                    "int": [
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
                },
                "defaults": {
                    "engine": [],
                    "based_in": [],
                    "seasons": [],
                    "antecedent_teams": [],
                },
            },
        )
        return cast("ConstructorRecord", payload)
