from __future__ import annotations

import ast
from dataclasses import dataclass
from pathlib import Path

SECTION_ROOT = Path("scrapers/parsers/section")

APPROVED_ROOT_BASES = {
    "SectionParserBase",
    "NestedWikiSectionParser",
    "SubSectionParser",
    "SubSubSectionParser",
}

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


@dataclass(frozen=True)
class ClassInfo:
    path: Path
    lineno: int
    bases: tuple[str, ...]


def _base_name(base: ast.expr) -> str:
    text = ast.unparse(base).split("[", 1)[0]
    return text.split(".")[-1]


def _load_classes() -> dict[str, ClassInfo]:
    classes: dict[str, ClassInfo] = {}
    for path in sorted(SECTION_ROOT.rglob("*.py")):
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in tree.body:
            if not isinstance(node, ast.ClassDef):
                continue
            if not (
                node.name.endswith("SectionParser") or node.name in APPROVED_ROOT_BASES
            ):
                continue
            classes[node.name] = ClassInfo(
                path=path,
                lineno=node.lineno,
                bases=tuple(_base_name(base) for base in node.bases),
            )
    return classes


def _descends_from_approved(
    cls_name: str,
    classes: dict[str, ClassInfo],
    seen: set[str] | None = None,
) -> bool:
    if cls_name in APPROVED_ROOT_BASES:
        return True
    if seen is None:
        seen = set()
    if cls_name in seen:
        return False
    seen.add(cls_name)

    info = classes.get(cls_name)
    if info is None:
        return cls_name in APPROVED_ROOT_BASES

    for base in info.bases:
        if base in APPROVED_ROOT_BASES:
            return True
        if base in classes and _descends_from_approved(base, classes, seen):
            return True
    return False


def test_section_parsers_inherit_only_from_approved_bases_and_mixins() -> None:
    classes = _load_classes()
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

        if not _descends_from_approved(class_name, classes):
            violations.append(
                f"{info.path}:{info.lineno} {class_name} does not descend from approved section parser bases",
            )

    assert not violations, "\n".join(violations)
