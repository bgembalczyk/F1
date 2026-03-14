from collections.abc import Callable
from collections.abc import Iterable
from collections.abc import Sequence
from dataclasses import dataclass
from typing import Any

from scrapers.base.helpers.text_normalization import to_snake_case
from scrapers.base.logging import get_logger

ParserType = Callable[[Any], Any] | str


@dataclass(frozen=True)
class InfoboxSchemaField:
    key: str
    labels: Sequence[str]
    parser: ParserType | None = None


class InfoboxSchema:
    """Schema mapująca etykiety infoboksa na spójne klucze."""

    def __init__(
        self,
        *,
        fields: Iterable[InfoboxSchemaField],
        name: str | None = None,
        required_keys: Iterable[str] | None = None,
        normalize_unknown: bool = True,
    ) -> None:
        self.name = name or "infobox"
        self.normalize_unknown = normalize_unknown
        self.fields = list(fields)
        self._label_map: dict[str, InfoboxSchemaField] = {}
        for field in self.fields:
            for label in field.labels:
                key = self._normalize_label(label)
                if key:
                    self._label_map[key] = field
        self.required_keys = (
            {key for key in required_keys}
            if required_keys is not None
            else {field.key for field in self.fields}
        )

    @staticmethod
    def _normalize_label(label: str) -> str:
        return label.strip().lower()

    def field_for_label(self, label: str | None) -> InfoboxSchemaField | None:
        if not label:
            return None
        return self._label_map.get(self._normalize_label(label))

    def normalize_label(self, label: str | None) -> str | None:
        if not label:
            return None
        field = self.field_for_label(label)
        if field is not None:
            return field.key
        if not self.normalize_unknown:
            return label
        normalized = to_snake_case(label)
        return normalized or None

    def normalize_rows(
        self,
        rows: dict[str, Any],
        *,
        logger=None,
        context: str | None = None,
    ) -> dict[str, Any]:
        normalized_rows: dict[str, Any] = {}
        for label, row in rows.items():
            key = self.normalize_label(label)
            if not key:
                continue
            if key in normalized_rows:
                if logger is None:
                    logger = get_logger(self.__class__.__name__)
                logger.debug(
                    "Duplicate infobox key %s for label %s (context=%s)",
                    key,
                    label,
                    context,
                )
                continue
            normalized_rows[key] = row
        return normalized_rows

    def log_missing(
        self,
        present_keys: Iterable[str],
        *,
        logger=None,
        context: str | None = None,
    ) -> None:
        if logger is None:
            return
        present_set = {key for key in present_keys if key}
        missing = sorted(self.required_keys - present_set)
        if missing:
            logger.info(
                "Missing infobox fields for %s: %s (context=%s)",
                self.name,
                ", ".join(missing),
                context,
            )
