from __future__ import annotations

from dataclasses import dataclass

from models.domain_model import DomainModel

from models.merge_types.constants import RecordDict
from models.merge_types.link_value import LinkValue


@dataclass(slots=True)
class TeamRecordModel(DomainModel):
    raw: RecordDict

    @classmethod
    def from_object(cls, value: object) -> TeamRecordModel | None:
        if not isinstance(value, dict):
            return None
        record: RecordDict = value
        return cls(raw=record)

    def dedupe_key(self) -> str | None:
        team = self.raw.get("team")
        team_link = LinkValue.from_object(team)
        if team_link is not None:
            return team_link.dedupe_key()

        if isinstance(team, str) and team:
            return team.casefold()

        return None

    def aliases(self) -> set[str]:
        aliases: set[str] = set()
        team = self.raw.get("team")
        team_link = LinkValue.from_object(team)
        if team_link is not None:
            if team_link.url:
                aliases.add(team_link.url)
            if team_link.text:
                aliases.add(team_link.text.casefold())

        if isinstance(team, str) and team:
            aliases.add(team.casefold())

        return aliases

    def to_dict(self) -> RecordDict:
        return self.raw
