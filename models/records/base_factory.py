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
from typing import cast

from models.mappers.field_aliases import apply_field_aliases
from models.records.factories import WIKI_SEASON_URL
from models.records.link import LinkRecord
from models.records.season import SeasonRecord
from models.validation.core import validate_float
from models.validation.core import validate_int
from models.validation.core import validate_status
from models.validation.validators import is_empty_link
from models.validation.validators import normalize_season_item
from models.validation.validators import validate_link
from models.validation.validators import validate_seasons

T = TypeVar("T")


class FieldNormalizer:
    """
    Service class for normalizing record fields.

    Provides reusable normalization methods following the Strategy pattern.
    Each method handles a specific field type (int, float, link, etc.).

    This is a Pure Fabrication (GRASP) - a service object that doesn't
    represent a domain concept but provides cohesive functionality.
    """

    @staticmethod
    def normalize_int(value: Any, field_name: str) -> int | None:
        """
        Normalize a value to integer, returning None on failure.

        Args:
            value: Value to normalize
            field_name: Name of field (for error context)

        Returns:
            Normalized integer or None
        """
        if value is None:
            return None
        try:
            return validate_int(value, field_name)
        except ValueError:
            return None

    @staticmethod
    def normalize_float(value: Any, field_name: str) -> float | None:
        """
        Normalize a value to float, returning None on failure.

        Args:
            value: Value to normalize
            field_name: Name of field (for error context)

        Returns:
            Normalized float or None
        """
        if value is None:
            return None
        try:
            return validate_float(value, field_name)
        except ValueError:
            return None

    @staticmethod
    def normalize_link(value: Any, field_name: str) -> LinkRecord | None:
        """
        Normalize a value to LinkRecord.

        Args:
            value: String or mapping containing link data
            field_name: Name of field (for error context)

        Returns:
            Normalized LinkRecord or None
        """
        normalized: LinkRecord | None = None

        if isinstance(value, str):
            text = value.strip()
            if text:
                normalized = {"text": text, "url": None}
        elif isinstance(value, Mapping):
            try:
                validated = validate_link(dict(value), field_name=field_name)
            except ValueError:
                validated = None
            if validated and not is_empty_link(validated):
                normalized = validated

        return normalized

    @staticmethod
    def normalize_link_list(value: Any, field_name: str) -> list[LinkRecord]:
        """
        Normalize a value to list of LinkRecords.

        Args:
            value: Single item or list of link data
            field_name: Name of field (for error context)

        Returns:
            List of normalized LinkRecords
        """
        if not value:
            return []
        items = value if isinstance(value, list) else [value]
        normalized_items: list[LinkRecord] = []
        for item in items:
            normalized = FieldNormalizer.normalize_link(item, field_name)
            if normalized is not None:
                normalized_items.append(normalized)
        return normalized_items

    @staticmethod
    def normalize_seasons(value: Any) -> list[SeasonRecord]:
        """
        Normalize a value to list of SeasonRecords.

        Args:
            value: Single season or list of seasons

        Returns:
            List of normalized SeasonRecords with URLs
        """
        if not value:
            return []
        try:
            if isinstance(value, list):
                seasons = validate_seasons(value)
            else:
                normalized = normalize_season_item(value)
                seasons = [normalized] if normalized else []
        except ValueError:
            return []

        # Add URLs for seasons that don't have them

        for season in seasons:
            if "url" not in season and "year" in season:
                season["url"] = WIKI_SEASON_URL.format(year=season["year"])

        return cast("list[SeasonRecord]", seasons)

    @staticmethod
    def normalize_status(
        value: Any,
        allowed: list[str],
        field_name: str,
    ) -> str | None:
        """
        Normalize a value to a status string from allowed values.

        Args:
            value: Value to normalize
            allowed: List of allowed status values
            field_name: Name of field (for error context)

        Returns:
            Normalized status or None
        """
        if value is None:
            return None
        try:
            return validate_status(value, allowed, field_name)
        except ValueError:
            return str(value).strip().lower() or None

    @staticmethod
    def normalize_string(value: Any) -> str | None:
        """
        Normalize a value to a string.

        Args:
            value: Value to normalize

        Returns:
            Trimmed string or None if empty
        """
        if value is None:
            return None
        if isinstance(value, str):
            return value.strip() or None
        return str(value).strip() or None

    @staticmethod
    def normalize_bool(value: Any) -> bool:
        """
        Normalize a value to boolean.

        Args:
            value: Value to normalize

        Returns:
            Boolean value
        """
        return bool(value)


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
