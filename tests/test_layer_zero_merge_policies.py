from layers.zero.merge_policies import DriversMergePolicy
from layers.zero.merge_policies import TeamsMergePolicy
from scrapers.wiki.constants import DRIVER_FATALITIES_SOURCE
from scrapers.wiki.constants import F1_DRIVERS_SOURCE
from scrapers.wiki.constants import FEMALE_DRIVERS_SOURCE
from scrapers.wiki.constants import PRIVATEER_TEAMS_SOURCE
from scrapers.wiki.constants import SPONSORSHIP_LIVERIES_SOURCE


def test_drivers_merge_policy_transforms_f1_driver_records() -> None:
    def _noop_attach(_: dict[str, object]) -> None:
        return None

    policy = DriversMergePolicy(
        transform_f1_driver=lambda record: {"driver": record.get("driver"), "ok": True},
        transform_female_driver=lambda record: record,
        attach_driver_death_data=_noop_attach,
    )

    assert policy.supports(F1_DRIVERS_SOURCE)
    assert policy.apply({"driver": "Max"}) == {"driver": "Max", "ok": True}


def test_drivers_merge_policy_transforms_female_records() -> None:
    def _noop_attach(_: dict[str, object]) -> None:
        return None

    policy = DriversMergePolicy(
        transform_f1_driver=lambda record: record,
        transform_female_driver=lambda record: {
            "driver": record.get("driver"),
            "gender": "female",
        },
        attach_driver_death_data=_noop_attach,
    )

    assert policy.supports(FEMALE_DRIVERS_SOURCE)
    assert policy.apply({"driver": "Maria"}) == {"driver": "Maria", "gender": "female"}


def test_drivers_merge_policy_attaches_fatality_data() -> None:
    def _attach(record: dict[str, object]) -> None:
        record["death"] = {"date": "2000-01-01"}

    policy = DriversMergePolicy(
        transform_f1_driver=lambda record: record,
        transform_female_driver=lambda record: record,
        attach_driver_death_data=_attach,
    )

    record = {"driver": "A"}
    assert policy.supports(DRIVER_FATALITIES_SOURCE)
    assert policy.apply(record) == {"driver": "A", "death": {"date": "2000-01-01"}}


def test_teams_merge_policy_handles_constructors_source() -> None:
    policy = TeamsMergePolicy(
        build_racing_series=lambda payload: {"formula_one": payload},
    )

    assert policy.supports("f1_constructors_2026.json")
    merged = policy.apply({"constructor": {"text": "Team X"}, "wins": 1})

    assert merged["team"] == {"text": "Team X"}
    assert merged["racing_series"] == {
        "formula_one": {"constructor": {"text": "Team X"}, "wins": 1},
    }


def test_teams_merge_policy_handles_sponsorship_liveries_source() -> None:
    policy = TeamsMergePolicy(
        build_racing_series=lambda payload: {"formula_one": payload},
    )

    assert policy.supports(SPONSORSHIP_LIVERIES_SOURCE)
    assert policy.apply({"team": "Ferrari", "liveries": ["Marlboro"]}) == {
        "team": "Ferrari",
        "racing_series": {"formula_one": {"liveries": ["Marlboro"]}},
    }


def test_teams_merge_policy_handles_privateer_source() -> None:
    policy = TeamsMergePolicy(
        build_racing_series=lambda payload: {"formula_one": payload},
    )

    assert policy.supports(PRIVATEER_TEAMS_SOURCE)
    assert policy.apply({"team": "Rob Walker", "seasons": ["1950"]}) == {
        "team": "Rob Walker",
        "racing_series": {"formula_one": {"seasons": ["1950"], "privateer": True}},
    }
