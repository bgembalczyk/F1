from __future__ import annotations

import ast
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class ClassInfo:
    module: str
    name: str
    bases: tuple[str, ...]
    parse_args: tuple[str, ...] | None
    is_protocol: bool
    is_abstract: bool


def _iter_parser_files(root: Path) -> list[Path]:
    return sorted((root / "scrapers" / "parsers").rglob("*.py"))


def _module_name(root: Path, file_path: Path) -> str:
    rel = file_path.relative_to(root).with_suffix("")
    return ".".join(rel.parts)


def _collect_classes(root: Path) -> dict[str, ClassInfo]:
    classes: dict[str, ClassInfo] = {}
    for py_file in _iter_parser_files(root):
        tree = ast.parse(py_file.read_text(encoding="utf-8"), filename=str(py_file))
        module = _module_name(root, py_file)
        for node in tree.body:
            if not isinstance(node, ast.ClassDef):
                continue

            parse_args: tuple[str, ...] | None = None
            is_protocol = any(
                ast.unparse(base).endswith("Protocol")
                or "Protocol[" in ast.unparse(base)
                for base in node.bases
            )
            is_abstract = any(ast.unparse(base).endswith("ABC") for base in node.bases)
            for member in node.body:
                if isinstance(member, ast.FunctionDef) and member.name == "parse":
                    parse_args = tuple(arg.arg for arg in member.args.args)
                    break

            key = f"{module}.{node.name}"
            classes[key] = ClassInfo(
                module=module,
                name=node.name,
                bases=tuple(
                    ast.unparse(base).split(".")[-1].split("[", 1)[0]
                    for base in node.bases
                ),
                parse_args=parse_args,
                is_protocol=is_protocol,
                is_abstract=is_abstract,
            )
    return classes


def _inherits_from(
    class_info: ClassInfo,
    classes_by_name: dict[str, ClassInfo],
    expected_bases: set[str],
) -> bool:
    pending = list(class_info.bases)
    seen: set[str] = set()
    while pending:
        base_name = pending.pop()
        if base_name in seen:
            continue
        seen.add(base_name)
        if base_name in expected_bases:
            return True
        for info in classes_by_name.values():
            if info.name == base_name:
                pending.extend(info.bases)
    return False


def _has_parse(
    class_info: ClassInfo,
    classes_by_name: dict[str, ClassInfo],
) -> bool:
    if class_info.parse_args is not None:
        return True
    pending = list(class_info.bases)
    seen: set[str] = set()
    while pending:
        base_name = pending.pop()
        if base_name in seen:
            continue
        seen.add(base_name)
        for info in classes_by_name.values():
            if info.name == base_name:
                if info.parse_args is not None:
                    return True
                pending.extend(info.bases)
    return False


def test_parser_name_to_inheritance_and_interface_contract() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    classes = _collect_classes(repo_root)
    violations: list[str] = []

    for class_info in classes.values():
        if class_info.is_protocol or class_info.is_abstract:
            continue

        if class_info.name.endswith("TableParser"):
            if class_info.module in {
                "scrapers.parsers.infobox.collapsible_table",
                "scrapers.parsers.infobox.table",
                # HtmlTableParser is a general-purpose HTML table parser,
                # not wiki-specific; excluded from wiki-table contract.
                "scrapers.parsers.html_table",
                "scrapers.parsers.table.html_table",
                # F1StandingsTableParser is a domain-specific standings parser
                # that operates on raw Tag input, not a wiki table mapper.
                "scrapers.parsers.section.standings.f1_table",
                # WikiTableParser IS the canonical table implementation
                "scrapers.parsers.wiki.table",
                "scrapers.parsers.wiki.table.__init__",
            }:
                continue
            base_name_join = " ".join(class_info.bases)
            _table_parser_bases = {
                "WikiTableBaseMapper",
                "WikiTableHtmlParser",
                "WikiTableParser",
            }
            inherits_table_base = _inherits_from(
                class_info,
                classes,
                _table_parser_bases,
            ) or any(b in base_name_join for b in _table_parser_bases)
            if not inherits_table_base:
                violations.append(
                    f"{class_info.module}.{class_info.name}: TableParser musi "
                    "dziedziczyć po WikiTableBaseMapper lub WikiTableHtmlParser",
                )
            if not _has_parse(class_info, classes):
                violations.append(
                    f"{class_info.module}.{class_info.name}: TableParser musi mieć "
                    "publiczne parse",
                )

        if class_info.name.endswith("Parser"):
            if not _inherits_from(class_info, classes, {"ParserABC"}):
                violations.append(
                    f"{class_info.module}.{class_info.name}: Parser musi "
                    "dziedziczyć po ParserABC (bezpośrednio lub pośrednio)",
                )
            if not _has_parse(class_info, classes):
                violations.append(
                    f"{class_info.module}.{class_info.name}: Parser musi mieć "
                    "publiczne parse (lokalnie lub przez dziedziczenie)",
                )

        if class_info.name.endswith("ListParser"):
            if class_info.name == "ListParser":
                continue
            if not _inherits_from(
                class_info,
                classes,
                {"ListParser", "ParserABC"},
            ):
                violations.append(
                    f"{class_info.module}.{class_info.name}: ListParser musi "
                    "dziedziczyć po ListParser lub ParserABC",
                )

        if class_info.name.endswith("SectionParser") and not class_info.name.endswith(
            "SubSectionParser",
        ):
            if (
                ".section.nested." in class_info.module
                or ".section.sublevels." in class_info.module
            ):
                continue
            if ".parsers.liveries." in class_info.module or class_info.module.endswith(
                ".section.sponsorship",
            ):
                continue
            if class_info.module.endswith(
                ".section.protocol",
            ) or class_info.module.endswith(
                ".section.section_parser_protocol",
            ):
                continue
            # Liveries / sponsorship section parsers use a different (soup-based)
            # interface and are governed by their own contracts.
            if class_info.module in {
                "scrapers.parsers.wiki.team_liveries_section",
                "scrapers.parsers.wiki.section.sponsorship",
            }:
                continue
            # RecursiveSectionParser is internal infrastructure for the nested-section
            # parsing engine and is not itself a user-facing concrete section parser.
            if class_info.module in {
                "scrapers.parsers.wiki.recursive",
            }:
                continue
            # The approved base classes themselves are self-referential in this check
            # and should be skipped.
            _section_parser_bases = {
                "SectionParser",
                "NestedWikiSectionParser",
                # Canonical runtime base for section parsers
                "SectionParserBase",
                # RecursiveSectionParser is now the canonical base for nested-section parsers
                "RecursiveSectionParser",
            }
            if class_info.name in _section_parser_bases:
                continue
            if not _inherits_from(class_info, classes, _section_parser_bases):
                violations.append(
                    f"{class_info.module}.{class_info.name}: SectionParser musi "
                    "realizować kontrakt SectionParser",
                )
            if class_info.parse_args is not None and (
                len(class_info.parse_args) < 2
                or class_info.parse_args[1] != "section_fragment"
            ):
                # NestedWikiSectionParser-style parsers accept a Tag/list[Tag] element,
                # not a section_fragment BeautifulSoup.  Skip the signature check for
                # the nested-parser base classes themselves and any parser that
                # descends from the nested-parser tree.
                _nested_roots = {
                    "NestedWikiSectionParser",
                    "SubSectionParser",
                    "SubSubSectionParser",
                    # RecursiveSectionParser is now the canonical base for nested parsers
                    "RecursiveSectionParser",
                }
                if class_info.name not in _nested_roots and not _inherits_from(
                    class_info,
                    classes,
                    _nested_roots,
                ):
                    violations.append(
                        f"{class_info.module}.{class_info.name}: parse musi mieć sygnaturę "
                        "parse(section_fragment)",
                    )

    assert not violations, "Naruszenia kontraktu parserów:\n- " + "\n- ".join(
        sorted(violations),
    )
