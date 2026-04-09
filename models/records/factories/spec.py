from typing import Any
from typing import Callable
from typing import TypedDict

from models.records.factories.base import BaseRecordFactory


class FactorySpec(TypedDict, total=False):
    aliases: dict[str, str]
    record_name: str
    field_normalizers: dict[str, Callable[[Any, str], Any]]
    list_field_normalizers: dict[str, list[str]]
    defaults: dict[str, Any]
    nested_factories: dict[str, BaseRecordFactory]
