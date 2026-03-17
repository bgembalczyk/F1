import re

MIN_RANGE_YEARS = 2
EXPECTED_STATS_COLUMNS = 3

MIN_LINKS_FOR_RANGE = 2
TWO_DIGIT_YEAR_SUFFIX = 2

MIN_VALID_CAR_NUMBER_YEAR = 1900

# Date pattern for matching common date formats
DATE_PATTERN = (
    r"\b\d{1,2}\s+[A-Za-z]+\s+\d{4}|\b[A-Za-z]+\s+\d{1,2},\s*\d{4}|\b\d{4}\b"
)

# Regex patterns for year detection (compiled once for performance)
FOUR_DIGIT_YEAR_PATTERN = re.compile(r"^(19|20)\d{2}$")
TWO_DIGIT_SUFFIX_PATTERN = re.compile(r"^\d{2}$")
