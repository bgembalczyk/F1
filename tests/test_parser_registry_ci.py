from __future__ import annotations

from scrapers.parsers.registry import REQUIRED_PRODUCTION_KEYS
from scrapers.parsers.registry import validate_parser_registry


def test_ci_production_parser_registry_is_complete() -> None:
    """CI gate: production parser keys muszą mieć wpisy w registry."""

    assert REQUIRED_PRODUCTION_KEYS
    validate_parser_registry(required_keys=REQUIRED_PRODUCTION_KEYS)
