from typing import Any

from scrapers.parsers.wiki.table.base import WikiTableBaseMapper


class BaseRedFlaggedRacesTableMapper(WikiTableBaseMapper):
    def map(self, table_data: dict[str, Any]) -> dict[str, Any] | None:
        result = super().map(table_data)
        if result is None:
            return None
        result["domain_rows"] = self._merge_failed_to_restart_rows(
            result["domain_rows"],
        )
        return result

    @staticmethod
    def _race_key(row: dict[str, Any]) -> tuple:
        raise NotImplementedError

    @classmethod
    def _merge_failed_to_restart_rows(
        cls,
        rows: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        merged: list[dict[str, Any]] = []
        for row in rows:
            raw_drivers = row.pop("failed_to_make_restart_drivers", None)
            drivers = raw_drivers if raw_drivers is not None else []
            reason = row.pop("failed_to_make_restart_reason", None)
            race_key = cls._race_key(row)
            has_data = bool(drivers or reason)
            entry = {"drivers": drivers, "reason": reason} if has_data else None
            if merged and cls._race_key(merged[-1]) == race_key:
                if entry is not None:
                    merged[-1]["failed_to_make_restart"].append(entry)
            else:
                row["failed_to_make_restart"] = [entry] if entry is not None else []
                merged.append(row)
        return merged
