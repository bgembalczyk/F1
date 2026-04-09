from validation.validator_base import ExportRecord


class EntriesStartsPointsPostProcessor:
    """Normalizes records from drivers list tables.

    Kept as a dedicated class so pipeline bindings can load it dynamically.
    """

    def post_process(self, records: list[ExportRecord]) -> list[ExportRecord]:
        return records
