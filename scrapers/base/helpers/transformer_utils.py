"""Utilities for applying record transformers."""

from typing import Any

from scrapers.base.transformers.helpers import apply_transformers
from scrapers.base.transformers.record_factory import RecordFactoryTransformer


def apply_transformers_with_factory(
    transformers: list[Any],
    record: dict[str, Any],
    record_factory: Any | None,
    logger: Any | None = None,
) -> Any:
    """
    Applies transformers to a record, optionally including a record factory transformer.

    Args:
        transformers: List of transformer instances to apply.
        record: The record to transform.
        record_factory: Optional factory to convert the record to a specific type.
        logger: Optional logger for warnings.

    Returns:
        The transformed record.
    """
    transformers_list = list(transformers)
    if record_factory is not None:
        transformers_list.append(
            RecordFactoryTransformer(
                record_factory,
                fallback_on_error=True,
            ),
        )
    if not transformers_list:
        return record
    transformed = apply_transformers(transformers_list, [record], logger=logger)
    return transformed[0] if transformed else {}
