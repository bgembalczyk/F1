"""Domain constants used across models and scrapers."""

# Statusy torów F1.
CIRCUIT_STATUS_CURRENT = "current"  # Tor używany aktualnie w kalendarzu.
CIRCUIT_STATUS_FUTURE = "future"  # Tor planowany/ogłoszony na przyszłość.
CIRCUIT_STATUS_FORMER = "former"  # Tor historyczny, nieużywany w kalendarzu.
ALLOWED_CIRCUIT_STATUSES = (
    CIRCUIT_STATUS_CURRENT,
    CIRCUIT_STATUS_FUTURE,
    CIRCUIT_STATUS_FORMER,
)

# Statusy producentów silników.
MANUFACTURER_STATUS_CURRENT = "current"  # Producent aktywny w F1.
MANUFACTURER_STATUS_FORMER = "former"  # Producent historyczny.
ALLOWED_MANUFACTURER_STATUSES = (
    MANUFACTURER_STATUS_CURRENT,
    MANUFACTURER_STATUS_FORMER,
)

# Statusy wyścigów (Grand Prix).
RACE_STATUS_ACTIVE = "active"  # Wyścig nadal występuje w kalendarzu.
RACE_STATUS_PAST = "past"  # Wyścig nie jest już rozgrywany.
ALLOWED_RACE_STATUSES = (
    RACE_STATUS_ACTIVE,
    RACE_STATUS_PAST,
)
