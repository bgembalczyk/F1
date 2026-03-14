"""Base record factory with common normalization patterns.

This module provides a base class for record factories
following DRY and SOLID principles.
Extracted common patterns from models/records/factories.py.

Follows SOLID principles:
- Single Responsibility: Handles only field normalization concerns
- DRY: Centralizes common normalization logic
- Open/Closed: Extensible through inheritance
"""

from collections.abc import Callable
from collections.abc import Mapping
from typing import Any
from typing import TypeVar

from models.mappers.field_aliases import apply_field_aliases
from models.records.field_normalizer import FieldNormalizer

T = TypeVar("T")


class BaseRecordFactory:
    """
    Base class for record factories providing common normalization utilities.

    Subclasses can use the provided normalization methods and hooks to build
    specific record types while avoiding code duplication.

    Follows the Template Method pattern - provides skeleton of algorithm
    with hooks for customization.
    """

    def __init__(self, normalizer: FieldNormalizer | None = None):
        """
        Initialize factory with optional custom normalizer.

        Args:
            normalizer: Custom field normalizer, or uses default
        """
        self.normalizer = normalizer or FieldNormalizer()

    def apply_aliases(
        self,
        record: Mapping[str, Any],
        aliases: dict[str, str],
        record_name: str,
    ) -> dict[str, Any]:
        """
        Apply field aliases to record.

        Args:
            record: Input record
            aliases: Mapping of alias names to canonical names
            record_name: Name of record type (for error messages)

        Returns:
            Record with aliases applied
        """
        return apply_field_aliases(record, aliases, record_name=record_name)

    def set_defaults(self, payload: dict[str, Any], defaults: dict[str, Any]) -> None:
        """
        Set default values for fields not present in payload.

        Args:
            payload: Record to update (modified in-place)
            defaults: Mapping of field names to default values
        """
        for key, default_value in defaults.items():
            payload.setdefault(key, default_value)

    def normalize_field(
        self,
        payload: dict[str, Any],
        field_name: str,
        normalizer: Callable[[Any, str], Any],
    ) -> None:
        """
        Normalize a single field in payload using provided normalizer.

        Args:
            payload: Record to update (modified in-place)
            field_name: Name of field to normalize
            normalizer: Function to normalize the field value
        """
        if field_name in payload:
            payload[field_name] = normalizer(payload[field_name], field_name)

    def normalize_fields(
        self,
        payload: dict[str, Any],
        field_specs: dict[str, Callable[[Any, str], Any]],
    ) -> None:
        """
        Normalize multiple fields in payload.

        Args:
            payload: Record to update (modified in-place)
            field_specs: Mapping of field names to normalizer functions
        """
        for field_name, normalizer in field_specs.items():
            self.normalize_field(payload, field_name, normalizer)
