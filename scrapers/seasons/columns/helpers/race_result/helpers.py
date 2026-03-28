from typing import Any


def append_note(result: dict[str, Any], note: str) -> None:
    notes = result.setdefault("notes", [])
    if note not in notes:
        notes.append(note)
