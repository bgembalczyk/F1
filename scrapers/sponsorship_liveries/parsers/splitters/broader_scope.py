from typing import Any


class BroaderScopeSplitter:
    def __init__(
        self,
        records: list[dict[str, Any]],
        season_scoped: list[dict[str, Any]],
    ) -> None:
        self._records = records
        self._season_scoped = season_scoped

    def split(self) -> list[dict[str, Any]]:
        result: list[dict[str, Any]] = []
        for record in self._records:
            if record.get("_season_scoped_gp"):
                result.append(self._without_marker(record))
                continue
            split_records = self._split_non_scoped_record(record)
            result.extend(split_records)
        return result

    @staticmethod
    def _without_marker(record: dict[str, Any]) -> dict[str, Any]:
        return {k: v for k, v in record.items() if k != "_season_scoped_gp"}

    def _split_non_scoped_record(self, record: dict[str, Any]) -> list[dict[str, Any]]:
        if self._should_skip_scope_split(record):
            return [record]

        record_years = self._years(record)
        if not record_years:
            return [record]

        scoped_years = self._overlapping_scoped_years(record_years)
        if not scoped_years:
            return [record]

        return self._build_split_result(record, record_years, scoped_years)

    @staticmethod
    def _should_skip_scope_split(record: dict[str, Any]) -> bool:
        return bool(record.get("driver"))

    def _build_split_result(
        self,
        record: dict[str, Any],
        record_years: set[int],
        scoped_years: set[int],
    ) -> list[dict[str, Any]]:
        split_result: list[dict[str, Any]] = []
        self._append_non_scoped_split(split_result, record, record_years - scoped_years)
        self._append_overlap_split(split_result, record, record_years & scoped_years)
        return split_result

    def _overlapping_scoped_years(self, record_years: set[int]) -> set[int]:
        scoped_years: set[int] = set()
        for scoped in self._season_scoped:
            years = self._years(scoped)
            if years & record_years:
                scoped_years |= years
        return scoped_years

    def _append_non_scoped_split(
        self,
        result: list[dict[str, Any]],
        record: dict[str, Any],
        years: set[int],
    ) -> None:
        if not years:
            return
        seasons = self._seasons_for_years(record, years)
        result.append({**record, "season": seasons})

    def _append_overlap_split(
        self,
        result: list[dict[str, Any]],
        record: dict[str, Any],
        years: set[int],
    ) -> None:
        if not years:
            return
        seasons = self._seasons_for_years(record, years)
        result.append(
            {**record, "season": seasons, "grand_prix_scope": {"type": "other"}},
        )

    @staticmethod
    def _years(record: dict[str, Any]) -> set[int]:
        return {
            s["year"]
            for s in (record.get("season") or [])
            if isinstance(s, dict) and "year" in s
        }

    @staticmethod
    def _seasons_for_years(
        record: dict[str, Any],
        years: set[int],
    ) -> list[dict[str, Any]]:
        return [
            s
            for s in (record.get("season") or [])
            if isinstance(s, dict) and s.get("year") in years
        ]
