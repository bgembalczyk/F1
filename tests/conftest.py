from __future__ import annotations

from pathlib import Path

import pytest

_MARKER_BY_PATTERN: tuple[tuple[str, str], ...] = (
    ("tests/contract/", "contract"),
    ("tests/architecture/", "architecture"),
    ("/test_architecture_", "architecture"),
    ("/test_domain_entrypoint_boundaries", "architecture"),
    ("/test_section_architecture_boundaries", "architecture"),
    ("/test_domain_minimal_e2e", "integration"),
    ("/test_driver_infobox_integration", "integration"),
    ("/test_section_adapter_integration", "integration"),
    ("/test_common_value_objects_integration", "integration"),
)


def _marker_for_path(path: str) -> str:
    """Map test file path to a run-profile marker.

    Konwencja markerów przypisuje dokładnie jeden marker profilowy na plik:
    - ``contract``: pliki pod ``tests/contract``;
    - ``architecture``: testy architektoniczne (katalog + nazwy plików);
    - ``integration``: testy integracyjne/E2E po nazwie pliku;
    - ``unit``: domyślnie dla pozostałych testów.
    """

    normalized = path.replace("\\", "/")
    if '/tests/' in normalized:
        normalized = normalized[normalized.index('/tests/') + 1 :]

    if not normalized.startswith("tests/"):
        return "unit"

    path_with_leading_slash = f"/{normalized}"
    for pattern, marker in _MARKER_BY_PATTERN:
        if pattern in normalized or pattern in path_with_leading_slash:
            return marker
    return "unit"


def pytest_collection_modifyitems(items: list[pytest.Item]) -> None:
    for item in items:
        marker = _marker_for_path(str(Path(item.fspath)))
        item.add_marker(getattr(pytest.mark, marker))
