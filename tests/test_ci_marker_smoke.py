import pytest

from layers.pipeline import RunProfile

pytestmark = pytest.mark.unit


def test_unit_marker_collection_smoke() -> None:
    assert RunProfile.DEBUG.value == "debug"
