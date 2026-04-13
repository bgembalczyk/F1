import ast

from pathlib import Path

from tests.architecture.class_info import ClassInfo

TARGET_BRANCHES = {
    "ParserABC",
    "HtmlTagParserABC",
    "HtmlSoupParserABC",
    "WikiTableElementParserABC",
    "WikiListElementParserABC",
    "WikiSectionElementParserABC",
    "WikiInfoboxElementParserABC",
    "WikiNavboxElementParserABC",
    "WikiFigureElementParserABC",
    "HtmlInfoboxFieldParser",
    "InfoboxRowsParser",
    # ABCs that serve as direct base contracts for concrete parsers
    "InfoboxFieldParserABC",  # legacy name kept for compatibility with historical checks
    "InfoboxHtmlFieldParserABC",
    "InfoboxRowsParserABC",
    "InfoboxNestedTableParserABC",
    "InfoboxCollapsibleTableParserABC",
    "TableParserABC",  # base of WikiTableBaseParser
}


ROOTS = (
    Path("scrapers/parsers/wiki"),
    Path("scrapers/parsers/infobox"),
    Path("scrapers/parsers/html_elements"),
    Path("scrapers/parsers/infobox/field"),
)

SECTION_ROOT = Path("scrapers/parsers/section")

APPROVED_ROOT_BASES = {
    "SectionParserBase",
    "NestedWikiSectionParser",
    "SubSectionParser",
    "SubSubSectionParser",
}

GROUP_KEYWORDS: tuple[str, ...] = (
    "table",
    "single",
    "factory",
    "helper",
    "validator",
)

PRODUCTION_ROOTS = (
    Path("layers"),
    Path("wiki_pipeline"),
    Path("complete_extractor"),
    Path("scrapers"),
    Path("models"),
    Path("validation"),
)

def base_name(base: ast.expr) -> str:
    text = ast.unparse(base)
    text = text.split("[", 1)[0]
    return text.split(".")[-1]


def all_parser_classes() -> dict[str, ClassInfo]:
    classes: dict[str, ClassInfo] = {}
    for root in ROOTS:
        for path in sorted(root.rglob("*.py")):
            tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
            for node in tree.body:
                if not isinstance(node, ast.ClassDef) or not node.name.endswith(
                    "Parser",
                ):
                    continue
                bases = tuple(base_name(base) for base in node.bases)
                has_parse = any(
                    isinstance(member, ast.FunctionDef) and member.name == "parse"
                    for member in node.body
                )
                classes[node.name] = ClassInfo(
                    name=node.name,
                    path=path,
                    lineno=node.lineno,
                    bases=bases,
                    has_parse=has_parse,
                )
    return classes


def is_target_candidate(info: ClassInfo) -> bool:
    path_str = info.path.as_posix()
    if "scrapers/parsers/infobox/" in path_str:
        return True
    if "infobox/field" in path_str:
        return True
    if not info.name.startswith("Wiki"):
        return False
    return any(
        token in info.name
        for token in ("Table", "List", "Section", "Infobox", "Navbox", "Figure")
    )


def descends_from_target(
    cls_name: str,
    classes: dict[str, ClassInfo],
    seen: set[str] | None = None,
) -> bool:
    if seen is None:
        seen = set()
    if cls_name in seen:
        return False
    seen.add(cls_name)

    info = classes.get(cls_name)
    if info is None:
        return cls_name in TARGET_BRANCHES

    for base in info.bases:
        if base in TARGET_BRANCHES:
            return True
        if base in classes and descends_from_target(base, classes, seen):
            return True
    return False


def has_parse_in_hierarchy(
    cls_name: str,
    classes: dict[str, ClassInfo],
    seen: set[str] | None = None,
) -> bool:
    if seen is None:
        seen = set()
    if cls_name in seen:
        return False
    seen.add(cls_name)

    info = classes.get(cls_name)
    if info is None:
        return cls_name in TARGET_BRANCHES

    if info.has_parse:
        return True

    return any(
        base in TARGET_BRANCHES
        or (base in classes and has_parse_in_hierarchy(base, classes, seen))
        for base in info.bases
    )

def load_classes() -> dict[str, ClassInfo]:
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
                bases=tuple(base_name(base) for base in node.bases),
            )
    return classes


def descends_from_approved(
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
        if base in classes and descends_from_approved(base, classes, seen):
            return True
    return False


def python_files() -> list[Path]:
    roots = ("scrapers", "tests")
    return [path for root in roots for path in Path(root).rglob("*.py")]


def is_protocol_base(base: ast.expr) -> bool:
    text = ast.unparse(base).split("[", 1)[0]
    return text.endswith("Protocol")

def is_tracked_group_file(path: Path) -> bool:
    return any(keyword in path.name for keyword in GROUP_KEYWORDS)


def looks_like_compat_module(path: Path) -> bool:
    lowered_parts = [part.lower() for part in path.parts]
    stem = path.stem.lower()
    token_in_stem = any(token in stem for token in ("compat", "shim", "alias"))
    token_in_parts = any(
        part in {"compat", "shim", "aliases"} for part in lowered_parts
    )
    return token_in_stem or token_in_parts


def iter_python_files() -> list[Path]:
    files: list[Path] = []
    for root in PRODUCTION_ROOTS:
        if not root.exists():
            continue
        files.extend(path for path in root.rglob("*.py") if path.is_file())
    return files


def is_compat_debt_module(module_name: str) -> bool:
    return (
        ".compat" in module_name
        or module_name.endswith("compat")
        or ".protocol2" in module_name
        or module_name.endswith("protocol2")
        or "_deprecated" in module_name
    )


def count_compat_debt_imports(tree: ast.AST) -> int:
    count = 0
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if is_compat_debt_module(alias.name):
                    count += 1
        elif isinstance(node, ast.ImportFrom):
            if is_compat_debt_module(node.module or ""):
                count += 1
    return count


def count_record_factory_aliases(tree: ast.AST) -> int:
    count = 0
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == "RecordFactory":
                    count += 1
    return count


