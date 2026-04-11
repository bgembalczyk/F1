from __future__ import annotations

from pathlib import Path

ALLOWED_ROOT_PARSER_MODULES: set[str] = {
    "scrapers/driver_ordered_table_parser.py",
    "scrapers/parser_table.py",
    "scrapers/parsers_points.py",
}


def test_no_new_parser_modules_in_scrapers_root() -> None:
    parser_modules = {path.as_posix() for path in Path("scrapers").glob("*parser*.py")}
    unexpected = sorted(parser_modules - ALLOWED_ROOT_PARSER_MODULES)
    assert not unexpected, (
        "New parser modules in scrapers/ root are forbidden. "
        "Move parser implementations under scrapers/parsers/.\n" + "\n".join(unexpected)
    )
