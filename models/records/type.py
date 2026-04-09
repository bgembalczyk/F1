from enum import Enum


class RecordType(str, Enum):
    LINK = "link"
    SEASON = "season"
    DRIVERS_CHAMPIONSHIPS = "drivers_championships"
    DRIVER = "driver"
    SPECIAL_DRIVER = "special_driver"
    CONSTRUCTOR = "constructor"
    CIRCUIT = "circuit"
    EVENT = "event"
    CAR = "car"
    FATALITY = "fatality"
    SEASON_SUMMARY = "season_summary"
    GRANDS_PRIX = "grands_prix"
    CIRCUIT_DETAILS = "circuit_details"
    CIRCUIT_COMPLETE = "circuit_complete"
    ENGINE_MANUFACTURER = "engine_manufacturer"


RECORD_TYPE_ALIASES: dict[str, str] = {
    "grand_prix": "grands_prix",
    "grandprix": "grands_prix",
}
