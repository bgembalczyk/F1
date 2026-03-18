from __future__ import annotations

from types import ModuleType

import pytest

from scrapers.wiki import discovery


def test_discovery_validation_fails_for_runner_without_metadata(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    fake_module = ModuleType("scrapers.fake.discovery_test")

    class NewRunner:
        pass

    NewRunner.__name__ = "NewRunner"
    NewRunner.__module__ = fake_module.__name__
    fake_module.NewRunner = NewRunner

    monkeypatch.setattr(
        discovery,
        "_iter_discovery_module_names",
        lambda: (fake_module.__name__,),
    )
    monkeypatch.setattr(discovery.importlib, "import_module", lambda _name: fake_module)

    with pytest.raises(ValueError, match="Discovery metadata missing"):
        discovery.validate_discovery_metadata_completeness()


