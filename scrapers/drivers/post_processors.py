from validation.records import ExportRecord


class EntriesStartsPointsPostProcessor:
    def post_process(self, records: list[ExportRecord]) -> list[ExportRecord]:
        for record in records:
            if not isinstance(record, dict):
                continue
            entries = record.get("entries")
            starts = record.get("starts")
            points = record.get("points")
            if (
                entries == 0
                and starts is not None
                and starts > 0
                and points is not None
            ):
                record["entries"] = starts
                record["starts"] = None
                record["points"] = None
        return records
