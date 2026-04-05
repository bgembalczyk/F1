from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

_MIN_DUPLICATE_SUFFIX_COUNT = 2


@dataclass(frozen=True)
class PathResolver:
    layer_zero_root: Path = Path("layers/0_layer")
    exports_root: Path = Path("data")
    debug_root: Path = Path("data/debug")

    def raw_dir(self, *, domain: str) -> Path:
        normalized_domain = _normalize_domain(domain)
        return self.layer_zero_root / normalized_domain / "A_scrape"

    def raw(self, *, domain: str, filename: str) -> Path:
        normalized_name = _normalize_output_name(filename)
        return self.raw_dir(domain=domain) / normalized_name

    def merged_dir(self, *, domain: str) -> Path:
        normalized_domain = _normalize_domain(domain)
        return self.layer_zero_root / normalized_domain / "B_merge"

    def merged(self, *, domain: str, filename: str | None = None) -> Path:
        normalized_domain = _normalize_domain(domain)
        merged_name = filename or f"{normalized_domain}.json"
        normalized_name = _normalize_output_name(merged_name)
        return self.merged_dir(domain=normalized_domain) / normalized_name

    def extract_dir(self, *, domain: str) -> Path:
        normalized_domain = _normalize_domain(domain)
        return self.layer_zero_root / normalized_domain / "C_extract"

    def extracted(self, *, domain: str, filename: str | None = None) -> Path:
        normalized_domain = _normalize_domain(domain)
        extracted_name = filename or f"{normalized_domain}.json"
        normalized_name = _normalize_output_name(extracted_name)
        return self.extract_dir(domain=normalized_domain) / normalized_name

    def d_merge_dir(self, *, domain: str) -> Path:
        normalized_domain = _normalize_domain(domain)
        return self.layer_zero_root / normalized_domain / "D_merge"

    def d_merged(self, *, domain: str, filename: str | None = None) -> Path:
        normalized_domain = _normalize_domain(domain)
        d_merged_name = filename or f"{normalized_domain}.json"
        normalized_name = _normalize_output_name(d_merged_name)
        return self.d_merge_dir(domain=normalized_domain) / normalized_name

    def debug(self, *parts: str) -> Path:
        return self.debug_root / _normalize_relative_parts(*parts)

    def exports(self, *parts: str) -> Path:
        return self.exports_root / _normalize_relative_parts(*parts)


DEFAULT_PATH_RESOLVER = PathResolver()


def format_domain_year_name(
    template: str,
    *,
    domain: str,
    year: int,
) -> str:
    _normalize_domain(domain)
    rendered = template.format(year=year, domain=domain)
    return _normalize_output_name(rendered)


def _normalize_domain(domain: str) -> str:
    normalized = domain.strip().replace("\\", "/")
    if not normalized:
        msg = "Domain cannot be empty."
        raise ValueError(msg)
    if "/" in normalized:
        msg = f"Domain must be a single path segment: {domain!r}."
        raise ValueError(msg)
    return normalized


def _normalize_output_name(filename: str) -> str:
    normalized = Path(str(filename).strip()).name
    if not normalized:
        msg = "Output filename cannot be empty."
        raise ValueError(msg)

    suffixes = Path(normalized).suffixes
    if len(suffixes) >= _MIN_DUPLICATE_SUFFIX_COUNT and suffixes[-1] == suffixes[-2]:
        msg = f"Output filename cannot use duplicated extension: {normalized!r}."
        raise ValueError(msg)

    return normalized


def _normalize_relative_parts(*parts: str) -> Path:
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
        _normalize_output_name(leaf)
    return normalized_path
