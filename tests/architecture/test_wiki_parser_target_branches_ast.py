from __future__ import annotations

import ast
from dataclasses import dataclass
from pathlib import Path

from tests.architecture.dummy_classes import ClassInfo
from tests.architecture.helpers import all_parser_classes
from tests.architecture.helpers import descends_from_target
from tests.architecture.helpers import has_parse_in_hierarchy
from tests.architecture.helpers import is_target_candidate


def test_wiki_parser_classes_follow_target_branches_and_parse_contract() -> None:
    classes = all_parser_classes()
    violations: list[str] = []

    for name, info in sorted(classes.items()):
        if not is_target_candidate(info):
            continue
        if not descends_from_target(name, classes):
            violations.append(
                f"{info.path}:{info.lineno} {name} does not inherit from target parser branches",
            )
            continue
        if not has_parse_in_hierarchy(name, classes):
            violations.append(
                f"{info.path}:{info.lineno} {name} has no parse in hierarchy",
            )

    assert not violations, "\\n".join(violations)
