import re

CLASSIFIED_DNF_MARK = "†"
CLASSIFIED_DNF_NOTE = "classified_after_dnf_90_percent"
CLASSIFIED_DNF_START_YEAR = 1985

SHARED_DRIVE_NO_POINTS_START_YEAR = 1960
SHARED_DRIVE_NO_POINTS_END_YEAR = 1964
SHARED_DRIVE_POINTS_START_YEAR = 1950
SHARED_DRIVE_POINTS_END_YEAR = 1957

FATAL_NOTES_START_YEAR = 1965
DOUBLE_POINTS_SEASON_YEAR = 2014
SPRINT_POINTS_START_YEAR = 2021

SHORT_HEX_COLOR_LENGTH = 3


# Pattern for range separators
SEPARATOR_PATTERN = re.compile(r"\s*[-—]\s*")


F2_INELIGIBLE_YEARS = {1957, 1958, 1966, 1967, 1969}


CLASSIFIED_DNF_BACKGROUNDS = {
    "Winner",
    "Second place",
    "Third place",
    "Other points position",
    "Other classified position",
}

BACKGROUND_TO_RESULT = {
    "ffffbf": "Winner",
    "dfdfdf": "Second place",
    "ffdf9f": "Third place",
    "dfffdf": "Other points position",
    "cfcfff": "Other classified position",
    "efcfff": "Not classified, retired",
    "ffcfcf": "Did not qualify",
    "000000": "Disqualified",
    "ffffff": "Did not start",
}
