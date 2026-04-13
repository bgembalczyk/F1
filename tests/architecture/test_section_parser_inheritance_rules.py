from __future__ import annotations

import ast
from dataclasses import dataclass
from pathlib import Path

from tests.architecture.dummy_classes import ClassInfo
from tests.architecture.helpers import descends_from_approved
from tests.architecture.helpers import load_classes

ALLOWED_MIXINS = {
    "ApplyForElementsMixin",
    "ExtractListItemsMixin",
}

DISALLOWED_BASES = {
    "SectionParserABC",
    "NestedSectionParserABC",
    "SubSectionParserABC",
    "SubSubSectionParserABC",
}


def test_section_parsers_inherit_only_from_approved_bases_and_mixins() -> None:
    classes = load_classes()
    violations: list[str] = []

    for class_name, info in sorted(classes.items()):
        for base in info.bases:
            if base in DISALLOWED_BASES:
                violations.append(
                    f"{info.path}:{info.lineno} {class_name} uses deprecated base {base}",
                )
            if base.endswith("Mixin") and base not in ALLOWED_MIXINS:
                violations.append(
                    f"{info.path}:{info.lineno} {class_name} uses disallowed mixin {base}",
                )

        if not descends_from_approved(class_name, classes):
            violations.append(
                f"{info.path}:{info.lineno} {class_name} does not descend from approved section parser bases",
            )

    assert not violations, "\n".join(violations)
