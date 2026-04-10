from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from path_resolver.helpers import normalize_domain
from path_resolver.helpers import normalize_output_name
from path_resolver.helpers import normalize_relative_parts


@dataclass(frozen=True)
class PathResolver:
    layer_zero_root: Path = Path("layers/0_layer")
    exports_root: Path = Path("data")
    debug_root: Path = Path("data/debug")

    def raw_dir(self, *, domain: str) -> Path:
        normalized_domain = normalize_domain(domain)
        return self.layer_zero_root / normalized_domain / "A_scrape"

    def raw(self, *, domain: str, filename: str) -> Path:
        normalized_name = normalize_output_name(filename)
        return self.raw_dir(domain=domain) / normalized_name

    def merged_dir(self, *, domain: str) -> Path:
        normalized_domain = normalize_domain(domain)
        return self.layer_zero_root / normalized_domain / "B_merge"

    def merged(self, *, domain: str, filename: str | None = None) -> Path:
        normalized_domain = normalize_domain(domain)
        merged_name = filename or f"{normalized_domain}.json"
        normalized_name = normalize_output_name(merged_name)
        return self.merged_dir(domain=normalized_domain) / normalized_name

    def extract_dir(self, *, domain: str) -> Path:
        normalized_domain = normalize_domain(domain)
        return self.layer_zero_root / normalized_domain / "C_extract"

    def extracted(self, *, domain: str, filename: str | None = None) -> Path:
        normalized_domain = normalize_domain(domain)
        extracted_name = filename or f"{normalized_domain}.json"
        normalized_name = normalize_output_name(extracted_name)
        return self.extract_dir(domain=normalized_domain) / normalized_name

    def d_merge_dir(self, *, domain: str) -> Path:
        normalized_domain = normalize_domain(domain)
        return self.layer_zero_root / normalized_domain / "D_merge"

    def d_merged(self, *, domain: str, filename: str | None = None) -> Path:
        normalized_domain = normalize_domain(domain)
        d_merged_name = filename or f"{normalized_domain}.json"
        normalized_name = normalize_output_name(d_merged_name)
        return self.d_merge_dir(domain=normalized_domain) / normalized_name

    def debug(self, *parts: str) -> Path:
        return self.debug_root / normalize_relative_parts(*parts)

    def exports(self, *parts: str) -> Path:
        return self.exports_root / normalize_relative_parts(*parts)


DEFAULT_PATH_RESOLVER = PathResolver()
