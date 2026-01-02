import re


def split_series(text: str) -> tuple[str, str | None]:
    parts = [p.strip() for p in re.split(r"\s*-\s*", text, maxsplit=1)]
    if len(parts) == 1:
        return text, None
    return parts[0], parts[1] or None
