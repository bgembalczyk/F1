from scrapers.base.constants.shared_headers import (
    SHARED_PODIUMS_HEADER as podiums_header,
)
from scrapers.base.constants.shared_headers import SHARED_POINTS_HEADER as points_header
from scrapers.base.constants.shared_headers import (
    SHARED_SEASONS_HEADER as seasons_header,
)

DRIVER_NAME_HEADER = "Driver name"
DRIVER_NATIONALITY_HEADER = "Nationality"
DRIVER_SEASONS_COMPETED_HEADER = "Seasons competed"
DRIVER_CHAMPIONSHIPS_HEADER = "Drivers' Championships"
DRIVER_RACE_ENTRIES_HEADER = "Race entries"
DRIVER_RACE_STARTS_HEADER = "Race starts"
DRIVER_POLE_POSITIONS_HEADER = "Pole positions"
DRIVER_RACE_WINS_HEADER = "Race wins"
DRIVER_PODIUMS_HEADER = podiums_header
DRIVER_FASTEST_LAPS_HEADER = "Fastest laps"
DRIVER_POINTS_HEADER = points_header

DRIVERS_LIST_HEADERS = [
    DRIVER_NAME_HEADER,
    DRIVER_NATIONALITY_HEADER,
    DRIVER_SEASONS_COMPETED_HEADER,
    DRIVER_CHAMPIONSHIPS_HEADER,
]

FATALITIES_SECTION_ID = "Detail_by_driver"
FATALITIES_DRIVER_HEADER = "Driver"
FATALITIES_DATE_HEADER = "Date of accident"
FATALITIES_AGE_HEADER = "Age"
FATALITIES_EVENT_HEADER = "Event"
FATALITIES_CIRCUIT_HEADER = "Circuit"
FATALITIES_CAR_HEADER = "Car"
FATALITIES_SESSION_HEADER = "Session"
FATALITIES_REF_HEADER = "Ref."  # Skrót od przypisów w tabeli.
FATALITIES_HEADERS = [
    FATALITIES_DRIVER_HEADER,
    FATALITIES_DATE_HEADER,
    FATALITIES_AGE_HEADER,
    FATALITIES_EVENT_HEADER,
    FATALITIES_CIRCUIT_HEADER,
    FATALITIES_CAR_HEADER,
    FATALITIES_SESSION_HEADER,
]

FEMALE_DRIVERS_SECTION_ID = "Official_drivers"
FEMALE_DRIVER_NAME_HEADER = "Name"
FEMALE_DRIVER_SEASONS_HEADER = seasons_header
FEMALE_DRIVER_TEAMS_HEADER = "Teams"
FEMALE_DRIVER_ENTRIES_STARTS_HEADER = "Entries (starts)"  # Łączone wpisy i starty.
FEMALE_DRIVER_POINTS_HEADER = points_header
FEMALE_DRIVERS_HEADERS = [
    FEMALE_DRIVER_NAME_HEADER,
    FEMALE_DRIVER_SEASONS_HEADER,
    FEMALE_DRIVER_TEAMS_HEADER,
    FEMALE_DRIVER_ENTRIES_STARTS_HEADER,
    FEMALE_DRIVER_POINTS_HEADER,
]

FEMALE_DRIVERS_INDEX_HEADER = "#"

MARK_ACTIVE_DRIVER = "~"  # Wiki oznacza aktywnego kierowcę.
MARK_ACTIVE_DRIVER_ALT = "*"  # Alternatywny znacznik aktywnego kierowcy w tabelach.
MARK_WORLD_CHAMPION = "^"  # Wiki oznacza mistrza świata.
MARK_F2_CATEGORY = "#"  # Symbol wiki wskazujący start w F2.
MARK_NON_CHAMPIONSHIP_EVENT = "†"  # Symbol wiki oznacza event poza cyklem mistrzostw.
