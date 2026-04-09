import importlib
from dataclasses import dataclass
from dataclasses import field
from typing import Any
from typing import Mapping

from scrapers.columns.base import BaseColumn


@dataclass(frozen=True)
class ColumnRef:
    class_path: str
    kwargs: Mapping[str, Any] = field(default_factory=dict)

    def build(self) -> BaseColumn:
        module_path, class_name = self.class_path.rsplit(".", 1)
        module = importlib.import_module(module_path)
        column_cls = getattr(module, class_name)
        if isinstance(column_cls, type) and issubclass(column_cls, BaseColumn):
            return column_cls(**dict(self.kwargs))
        if callable(column_cls):
            instance = column_cls(**dict(self.kwargs))
            if isinstance(instance, BaseColumn):
                return instance
        msg = f"{self.class_path} is not a BaseColumn factory or subclass."
        raise TypeError(msg)

    @classmethod
    def from_instance(cls, column: BaseColumn) -> "ColumnRef":
        class_path = f"{column.__class__.__module__}.{column.__class__.__name__}"
        kwargs = dict(getattr(column, "__dict__", {}))
        return cls(class_path=class_path, kwargs=kwargs)

