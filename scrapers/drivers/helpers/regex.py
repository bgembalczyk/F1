import re

UNIT_RE = re.compile(
    r"(?P<value>[-+]?\d[\d,]*(?:\.\d+)?)\s*"
    r"(?P<unit>cm³|cm3|cc|l|litre|litres)\b",
    flags=re.IGNORECASE,
)
ANGLE_RE = re.compile(
    r"(?P<value>[-+]?\d[\d,]*(?:\.\d+)?)\s*(?:°|deg|degrees?)",
    flags=re.IGNORECASE,
)
CONFIG_TYPE_RE = re.compile(r"\b([A-Z]{1,2}\d+)\b")
RANGE_RE = re.compile(
    r"(?P<min>[-+]?\d[\d,]*(?:\.\d+)?)\s*[–-]\s*(?P<max>[-+]?\d[\d,]*(?:\.\d+)?)",
    flags=re.IGNORECASE,
)
