DRIVER_FAMILY_BASE = "driver_summary"
DRIVER_FAMILY_EXTENSIONS = frozenset({"driver_details", "driver_complete"})

CONSTRUCTOR_FAMILY_BASE = "constructor_summary"
CONSTRUCTOR_FAMILY_EXTENSIONS = frozenset(
    {"constructor_details", "constructor_complete"},
)

CIRCUIT_FAMILY_BASE = "circuit_summary"
CIRCUIT_FAMILY_EXTENSIONS = frozenset({"circuit_details", "circuit_complete"})

RECORD_FAMILY_TAXONOMY = {
    "driver": {
        "base": DRIVER_FAMILY_BASE,
        "extensions": DRIVER_FAMILY_EXTENSIONS,
    },
    "constructor": {
        "base": CONSTRUCTOR_FAMILY_BASE,
        "extensions": CONSTRUCTOR_FAMILY_EXTENSIONS,
    },
    "circuit": {
        "base": CIRCUIT_FAMILY_BASE,
        "extensions": CIRCUIT_FAMILY_EXTENSIONS,
    },
}

__all__ = [
    "DRIVER_FAMILY_BASE",
    "DRIVER_FAMILY_EXTENSIONS",
    "CONSTRUCTOR_FAMILY_BASE",
    "CONSTRUCTOR_FAMILY_EXTENSIONS",
    "CIRCUIT_FAMILY_BASE",
    "CIRCUIT_FAMILY_EXTENSIONS",
    "RECORD_FAMILY_TAXONOMY",
]
