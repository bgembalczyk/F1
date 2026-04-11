def seasons_key(seasons: list[dict] | None) -> tuple | None:
    if not seasons:
        return None
    return tuple((season.get("year"), season.get("url")) for season in seasons)


def extract_first_place_role(first_place: object) -> tuple[str | None, int | None]:
    if isinstance(first_place, dict) and "role" in first_place:
        return first_place.get("role"), first_place.get("value")
    return None, first_place if isinstance(first_place, int) else None
