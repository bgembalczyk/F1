from pathlib import Path

MIN_DUPLICATE_SUFFIX_COUNT = 2


def format_domain_year_name(
    template: str,
    *,
    domain: str,
    year: int,
) -> str:
    normalize_domain(domain)
    rendered = template.format(year=year, domain=domain)
    return normalize_output_name(rendered)


def normalize_domain(domain: str) -> str:
    normalized = domain.strip().replace("\\", "/")
    if not normalized:
        msg = "Domain cannot be empty."
        raise ValueError(msg)
    if "/" in normalized:
        msg = f"Domain must be a single path segment: {domain!r}."
        raise ValueError(msg)
    return normalized


def normalize_output_name(filename: str) -> str:
    normalized = Path(str(filename).strip()).name
    if not normalized:
        msg = "Output filename cannot be empty."
        raise ValueError(msg)

    suffixes = Path(normalized).suffixes
    if len(suffixes) >= MIN_DUPLICATE_SUFFIX_COUNT and suffixes[-1] == suffixes[-2]:
        msg = f"Output filename cannot use duplicated extension: {normalized!r}."
        raise ValueError(msg)

    return normalized


def normalize_relative_parts(*parts: str) -> Path:
    if not parts:
        msg = "At least one output path segment is required."
        raise ValueError(msg)

    normalized_parts: list[str] = []
    for raw_part in parts:
        part = str(raw_part).strip().replace("\\", "/")
        if not part:
            msg = "Output path segment cannot be empty."
            raise ValueError(msg)
        part_path = Path(part)
        if part_path.is_absolute() or ".." in part_path.parts:
            msg = f"Output path segment must stay relative: {raw_part!r}."
            raise ValueError(msg)
        normalized_parts.append(part)

    normalized_path = Path(*normalized_parts)
    leaf = normalized_path.name
    if "." in leaf:
        normalize_output_name(leaf)
    return normalized_path
