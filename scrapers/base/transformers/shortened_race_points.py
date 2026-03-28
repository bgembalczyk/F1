from scrapers.base.transformers.record_transformer import RecordTransformer


class ShortenedRacePointsTransformer(RecordTransformer):
    def transform(self, records: list[dict]) -> list[dict]:
        grouped: list[dict] = []
        index: dict[tuple, int] = {}

        for record in records:
            seasons = record.get("seasons", [])
            key = tuple((season.get("year"), season.get("url")) for season in seasons)
            if key not in index:
                grouped.append(
                    {
                        "seasons": seasons,
                        "race_length_points": [],
                    },
                )
                index[key] = len(grouped) - 1

            grouped[index[key]]["race_length_points"].append(
                {key: value for key, value in record.items() if key != "seasons"},
            )

        return grouped
