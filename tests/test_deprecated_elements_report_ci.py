from __future__ import annotations

from scrapers.cli import MODULE_DEFINITIONS


def test_no_deprecated_metadata_in_cli_registry() -> None:
    assert MODULE_DEFINITIONS
    for definition in MODULE_DEFINITIONS.values():
        assert not hasattr(definition, "deprecated")
