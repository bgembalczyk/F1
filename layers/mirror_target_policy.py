from __future__ import annotations

from collections.abc import Mapping
from pathlib import Path


class MirrorTargetPolicy:
    def __init__(
        self,
        *,
        target_templates_by_source_category: Mapping[str, tuple[tuple[str, str], ...]],
    ) -> None:
        self._target_templates_by_source_category = target_templates_by_source_category

    def targets_for(self, *, source_category: str, year: int) -> tuple[Path, ...]:
        target_templates = self._target_templates_by_source_category.get(
            source_category,
            (),
        )
        return tuple(
            Path("layers")
            / "0_layer"
            / target_category
            / "raw"
            / target_name_template.format(year=year)
            for target_category, target_name_template in target_templates
        )
