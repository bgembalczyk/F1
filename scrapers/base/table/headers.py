from scrapers.base.helpers.text import strip_marks


def normalize_header(header: str) -> str:
    return (
        strip_marks(header)
        .strip()
        .lower()
        .replace("\u2019", "'")
        .replace(" ", "_")
        .replace("(", "")
        .replace(")", "")
        .replace("/", "_")
    )
