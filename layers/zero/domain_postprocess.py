import logging
from collections.abc import Callable

from layers.zero.record_merge_ops import merge_duplicate_records
from layers.zero.record_merge_ops import merge_values
from models.merge_types.record.driver import DriverRecordModel
from models.merge_types.record.season import SeasonRecordModel
from models.merge_types.record.team import TeamRecordModel
from scrapers.constants.constants_wiki import CHASSIS_CONSTRUCTOR_DOMAINS

DomainRecordsProcessor = Callable[[list[object]], list[object]]

logger = logging.getLogger(__name__)
MIN_YEAR_DIGITS = 4


def normalized_text(value: object) -> str:
    text_value = value.get("text", "") if isinstance(value, dict) else value or ""
    return str(text_value).strip().casefold()


def sort_key_with_presence(value: object) -> tuple[int, str]:
    text = normalized_text(value)
    return (0, text) if text else (1, "")


def season_year_func(season: object) -> int | None:
    if isinstance(season, int):
        return season
    if not isinstance(season, dict):
        return None

    direct_year = season.get("year")
    if isinstance(direct_year, int):
        return direct_year

    text_year = season.get("text")
    if isinstance(text_year, str):
        year = "".join(ch for ch in text_year if ch.isdigit())
        if len(year) >= MIN_YEAR_DIGITS:
            return int(year[:4])
    return None


def season_sort_key(record: object) -> tuple[int, str]:
    if not isinstance(record, dict):
        return (1, "")

    season_year = season_year_func(record.get("season"))
    if season_year is not None:
        return (0, str(season_year).zfill(10))
    return (1, "")


def driver_sort_key(record: object) -> str:
    if not isinstance(record, dict):
        return ""

    driver_value = record.get("driver")
    if isinstance(driver_value, dict):
        driver_text = str(driver_value.get("text", ""))
    else:
        driver_text = str(driver_value or "")

    name_parts = driver_text.split(" ", 1)
    if len(name_parts) == 1:
        return driver_text.strip().casefold()
    return name_parts[1].strip().casefold()


def constructor_sort_key(record: object) -> str:
    if not isinstance(record, dict):
        return ""
    constructor = record.get("constructor")
    if isinstance(constructor, dict):
        chassis = normalized_text(constructor.get("chassis_constructor"))
        engine = normalized_text(constructor.get("engine_constructor"))
        if chassis or engine:
            return f"{chassis}\u0000{engine}"
    return normalized_text(constructor)


def chassis_constructor_sort_key(record: object) -> str:
    if not isinstance(record, dict):
        return ""
    return normalized_text(record.get("chassis_constructor"))


def circuits_sort_key(record: object) -> str:
    if not isinstance(record, dict):
        return ""
    return normalized_text(record.get("circuit"))


def team_sort_key(record: object) -> str:
    if not isinstance(record, dict):
        return ""
    team_value = record.get("team")
    if team_value is not None:
        return normalized_text(team_value)
    return normalized_text(record.get("text"))


def engine_sort_key(record: object) -> str:
    if not isinstance(record, dict):
        return ""
    engine_constructor = record.get("engine_constructor")
    if engine_constructor is not None:
        return normalized_text(engine_constructor)
    return normalized_text(record.get("manufacturer"))


def grands_prix_sort_key(record: object) -> str:
    if not isinstance(record, dict):
        return ""
    return normalized_text(record.get("race_title"))


def races_sort_key(record: object) -> tuple[int, str, int, str]:
    if not isinstance(record, dict):
        return (1, "", 1, "")

    season_key = sort_key_with_presence(record.get("season"))
    grand_prix = record.get("grand_prix")
    if grand_prix is None:
        grand_prix = record.get("event")
    grand_prix_key = sort_key_with_presence(grand_prix)
    return season_key + grand_prix_key


def merge_duplicate_drivers(records: list[object]) -> list[object]:
    return merge_duplicate_records(records, DriverRecordModel, merge_values)


def merge_duplicate_teams(records: list[object]) -> list[object]:
    return merge_duplicate_records(records, TeamRecordModel, merge_values)


def season_years(value: object) -> set[int]:
    years: set[int] = set()
    if (season := SeasonRecordModel.from_object(value)) is not None:
        if (year := season.year()) is not None:
            years.add(year)
        return years

    if isinstance(value, list):
        for item in value:
            years.update(season_years(item))

    return years


def nest_team_liveries(items: list[object]) -> list[object]:
    return [nest_team_liveries_in_seasons(record) for record in items]


def nest_team_liveries_in_seasons(record: object) -> object:
    if not isinstance(record, dict):
        return record
    racing_series = record.get("racing_series")
    if not isinstance(racing_series, dict):
        return record
    formula_one = racing_series.get("formula_one")
    if not isinstance(formula_one, dict):
        return record

    seasons = formula_one.get("seasons")
    liveries = formula_one.get("liveries")
    if not isinstance(seasons, list) or not isinstance(liveries, list):
        return record

    remaining_liveries = attach_liveries_to_matching_seasons(
        seasons=seasons,
        liveries=liveries,
    )

    if remaining_liveries:
        formula_one["liveries"] = remaining_liveries
    else:
        formula_one.pop("liveries", None)
    return record


def attach_liveries_to_matching_seasons(
    *,
    seasons: list[object],
    liveries: list[object],
) -> list[object]:
    remaining_liveries: list[object] = []
    for livery in liveries:
        if not isinstance(livery, dict):
            remaining_liveries.append(livery)
            continue
        if not livery_matches_any_season(seasons=seasons, livery=livery):
            remaining_liveries.append(livery)
    return remaining_liveries


def livery_matches_any_season(
    *,
    seasons: list[object],
    livery: dict[str, object],
) -> bool:
    livery_years = season_years(livery.get("season"))
    livery_payload = {key: value for key, value in livery.items() if key != "season"}
    matched = False
    for season in seasons:
        season_record = SeasonRecordModel.from_object(season)
        if season_record is None:
            continue
        season_year = season_record.year()
        if season_year is None or season_year not in livery_years:
            continue
        matched = True
        season_record.append_livery(livery_payload)
    return matched


def merge_duplicate_seasons(items: list[object]) -> list[object]:
    merged_records: list[object] = []
    index_by_year: dict[int, int] = {}
    for item in items:
        if not isinstance(item, dict):
            merged_records.append(item)
            continue
        record_year = season_year_func(item.get("season"))
        if record_year is None:
            merged_records.append(item)
            continue

        existing_index = index_by_year.get(record_year)
        if existing_index is None:
            index_by_year[record_year] = len(merged_records)
            merged_records.append(item)
            continue

        existing_record = merged_records[existing_index]
        if isinstance(existing_record, dict):
            merged_records[existing_index] = merge_values(existing_record, item)

    return merged_records


def sort(items: list[object], sort_key: Callable[[object], object]) -> list[object]:
    return sorted(items, key=sort_key)


def records_debug_summary(records: list[object]) -> str:
    sample = records[0] if records else None
    sample_type = type(sample).__name__ if sample is not None else "none"
    return f"count={len(records)}, first_type={sample_type}"


def configure_domain_postprocessors(
    domain_pipeline_configs: dict[str, object],
    domain_pipeline_config_factory: type,
) -> None:
    postprocess_steps: dict[str, tuple[tuple[str, DomainRecordsProcessor], ...]] = {
        "circuits": (
            ("sort_circuits_by_name", lambda items: sort(items, circuits_sort_key)),
        ),
        "countries": (
            (
                "sort_countries_by_text",
                lambda items: sort(items, sort_key_with_presence),
            ),
        ),
        "drivers": (
            ("merge_duplicate_drivers", merge_duplicate_drivers),
            ("sort_drivers_by_name", lambda items: sort(items, driver_sort_key)),
        ),
        "teams": (
            ("merge_duplicate_teams", merge_duplicate_teams),
            ("nest_team_liveries", nest_team_liveries),
            ("sort_teams_by_name", lambda items: sort(items, team_sort_key)),
        ),
        "engines": (
            (
                "sort_engines_by_manufacturer",
                lambda items: sort(items, engine_sort_key),
            ),
        ),
        "seasons": (
            ("merge_duplicate_seasons", merge_duplicate_seasons),
            ("sort_seasons_by_year", lambda items: sort(items, season_sort_key)),
        ),
        "grands_prix": (
            (
                "sort_grands_prix_by_race_title",
                lambda items: sort(items, grands_prix_sort_key),
            ),
        ),
        "races": (
            (
                "sort_races_by_season_and_grand_prix",
                lambda items: sort(items, races_sort_key),
            ),
        ),
        "sponsors": (
            (
                "sort_sponsors_by_text",
                lambda items: sort(items, sort_key_with_presence),
            ),
        ),
        "chassis_constructors": (
            (
                "sort_chassis_constructors_by_name",
                lambda items: sort(items, chassis_constructor_sort_key),
            ),
        ),
    }

    for constructor_domain in CHASSIS_CONSTRUCTOR_DOMAINS:
        postprocess_steps.setdefault(
            constructor_domain,
            (
                (
                    "sort_constructors_by_name",
                    lambda items: sort(items, constructor_sort_key),
                ),
            ),
        )

    for domain, steps in postprocess_steps.items():
        existing = domain_pipeline_configs.get(domain, domain_pipeline_config_factory())
        domain_pipeline_configs[domain] = domain_pipeline_config_factory(
            transformers=existing.transformers,
            postprocessors=steps,
            records_normalizer=existing.records_normalizer,
        )


def post_process_domain_records(
    domain: str,
    records: list[object],
    domain_pipeline_configs: dict[str, object],
    domain_pipeline_config_factory: type,
) -> list[object]:
    postprocessors = domain_pipeline_configs.get(
        domain,
        domain_pipeline_config_factory(),
    ).postprocessors

    current = records
    executed_steps: list[str] = []
    for step_name, step_processor in postprocessors:
        before_summary = records_debug_summary(current)
        current = step_processor(current)
        after_summary = records_debug_summary(current)
        executed_steps.append(step_name)
        logger.debug(
            "Domain '%s' postprocess step '%s': %s -> %s",
            domain,
            step_name,
            before_summary,
            after_summary,
        )

    logger.debug(
        "Domain '%s' postprocess steps executed (order=%s, final_count=%s)",
        domain,
        executed_steps,
        len(current),
    )
    return current
