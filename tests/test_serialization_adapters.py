import pytest

from models.mappers.serialization import clear_serializable_adapters
from models.mappers.serialization import register_serializable_adapter
from models.mappers.serialization import SerializableProtocol
from models.mappers.serialization import to_dict


@pytest.fixture(autouse=True)
def reset_serializable_adapters():
    clear_serializable_adapters()
    yield
    clear_serializable_adapters()


class SerializableModel(SerializableProtocol):
    def to_serializable(self) -> dict[str, str]:
        return {"source": "protocol"}


class DumpModel:
    def model_dump(self):
        return {"source": "dump"}


class DictModel:
    def dict(self):
        return {"source": "dict"}


def test_to_dict_uses_serializable_protocol():
    assert to_dict(SerializableModel()) == {"source": "protocol"}


def test_to_dict_requires_adapter_for_non_contract_models():
    with pytest.raises(TypeError, match="Nieobsługiwany typ modelu"):
        to_dict(DumpModel())
    with pytest.raises(TypeError, match="Nieobsługiwany typ modelu"):
        to_dict(DictModel())


def test_to_dict_uses_registered_adapter_for_non_contract_models():
    register_serializable_adapter(
        DumpModel,
        lambda value: value.model_dump(),
    )

    assert to_dict(DumpModel()) == {"source": "dump"}
