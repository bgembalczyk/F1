from dataclasses import dataclass

from pathlib import Path


@dataclass(frozen=True)
class ClassInfo:
    name: str | None
    path: Path
    lineno: int
    bases: tuple[str, ...]
    has_parse: bool | None

