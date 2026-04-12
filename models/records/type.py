from enum import Enum


class RecordType(str, Enum):
    LINK = "link"
    SEASON = "season"
    DRIVERS_CHAMPIONSHIPS = "drivers_championships"
    DRIVER = "driver"
    DRIVER_SUMMARY = "driver_summary"
    DRIVER_DETAILS = "driver_details"
    DRIVER_COMPLETE = "driver_complete"
    SPECIAL_DRIVER = "special_driver"
    CONSTRUCTOR = "constructor"
    CONSTRUCTOR_SUMMARY = "constructor_summary"
    CONSTRUCTOR_DETAILS = "constructor_details"
    CONSTRUCTOR_COMPLETE = "constructor_complete"
    CIRCUIT = "circuit"
    CIRCUIT_SUMMARY = "circuit_summary"
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
    "driver": "driver",
    "constructor": "constructor",
    "circuit": "circuit",
    "driver_summary": "driver",
    "constructor_summary": "constructor",
    "circuit_summary": "circuit",
    "driver_base": "driver",
    "constructor_base": "constructor",
    "circuit_base": "circuit",
}
