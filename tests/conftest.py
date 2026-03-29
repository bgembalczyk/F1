from __future__ import annotations

import pytest


_UNIT_SMOKE_TESTS = {
    "tests/test_layer_zero_record_transform_handlers.py",
    "tests/test_transformers_pipeline.py",
}


def pytest_collection_modifyitems(items: list[pytest.Item]) -> None:
    """Backfill marks used by CI marker expressions for stable smoke tests."""
    for item in items:
        path = str(item.fspath)
        if any(path.endswith(test_path) for test_path in _UNIT_SMOKE_TESTS):
            item.add_marker(pytest.mark.unit)
