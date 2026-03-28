from typing import Any


class GrandPrixScopeAccumulator:
    def __init__(self) -> None:
        self.entries: list[dict[str, Any]] = []
        self.has_onwards = False
        self.range_scope: dict[str, Any] | None = None
        self.invalid = False

    def build_scope(self) -> dict[str, Any] | None:
        if self.range_scope:
            return self.range_scope
        if self.has_onwards and self.entries:
            return {"type": "range", "from": self.entries[0], "to": None}
        if self.entries:
            return {"type": "only", "grand_prix": self.entries}
        return None
