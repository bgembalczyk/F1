from scrapers.base.transformers.record_transformer import RecordTransformer
from scrapers.points.parsers import extract_first_place_role
from scrapers.points.parsers import seasons_key


class PointsScoringSystemsHistoryTransformer(RecordTransformer):
    def transform(self, records: list[dict]) -> list[dict]:
        merged: list[dict] = []
        merged_by_seasons: dict[tuple | None, dict] = {}

        for record in records:
            first_place = record.get("1st")
            role, value = extract_first_place_role(first_place)
            key = seasons_key(record.get("seasons"))

            if role:
                existing = merged_by_seasons.get(key)
                if existing is None:
                    merged_record = dict(record)
                    merged_record["1st"] = {role: value}
                    merged_by_seasons[key] = merged_record
                    merged.append(merged_record)
                else:
                    merged_first = existing.get("1st")
                    merged_first = (
                        dict(merged_first) if isinstance(merged_first, dict) else {}
                    )
                    merged_first[role] = value
                    existing["1st"] = merged_first
                continue

            if key not in merged_by_seasons:
                merged_by_seasons[key] = record
                merged.append(record)

        return merged
