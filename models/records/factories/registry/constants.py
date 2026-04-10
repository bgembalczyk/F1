from typing import Final

CRITICAL_RECORD_TYPES: Final[frozenset[str]] = frozenset(
    {
        "drivers_championships",
    },
)
FACTORY_MARKER_ATTR: Final[str] = "__factory_registry_record_type__"
