import re

FRACTION_RE = re.compile(
    r"(?:(?P<whole>\d+)\s+)?(?P<numerator>\d+)\s*[/]\s*(?P<denominator>\d+)",
)
POINTS_WITH_TOTAL_RE = re.compile(r"^(.*?)\(([^)]+)\)")
MARKS_RE = re.compile(r"[†‡✝✚*~^]")
SPLIT_RESULTS_RE = re.compile(r"\s*/\s*")

TYRE_NAME_BY_CODE = {
    "A": "Avon",
    "B": "Bridgestone",
    "C": "Continental",
    "D": "Dunlop",
    "E": "Englebert",
    "F": "Firestone",
    "G": "Goodyear",
    "M": "Michelin",
    "P": "Pirelli",
}
