# ruff: noqa: E501, PLR2004
import pytest

from pathlib import Path

from layers.path_resolver import DEFAULT_PATH_RESOLVER
from layers.path_resolver import PathResolver
from layers.path_resolver import _normalize_domain
from layers.path_resolver import _normalize_output_name
from layers.path_resolver import _normalize_relative_parts


def test_default_exports_root_points_to_data_directory() -> None:
    assert DEFAULT_PATH_RESOLVER.exports_root == Path("data")


# merged() paths
def test_merged_uses_domain_name_when_no_filename() -> None:
    resolver = PathResolver()
    result = resolver.merged(domain="drivers")
    assert result == Path("layers/0_layer/drivers/B_merge/drivers.json")


def test_merged_uses_explicit_filename() -> None:
    resolver = PathResolver()
    result = resolver.merged(domain="drivers", filename="custom.json")
    assert result == Path("layers/0_layer/drivers/B_merge/custom.json")


# extracted() paths
def test_extracted_uses_domain_name_when_no_filename() -> None:
    resolver = PathResolver()
    result = resolver.extracted(domain="circuits")
    assert result == Path("layers/0_layer/circuits/C_extract/circuits.json")


def test_extracted_uses_explicit_filename() -> None:
    resolver = PathResolver()
    result = resolver.extracted(domain="circuits", filename="output.json")
    assert result == Path("layers/0_layer/circuits/C_extract/output.json")


# d_merged() paths
def test_d_merged_uses_domain_name_when_no_filename() -> None:
    resolver = PathResolver()
    result = resolver.d_merged(domain="teams")
    assert result == Path("layers/0_layer/teams/D_merge/teams.json")


def test_d_merged_uses_explicit_filename() -> None:
    resolver = PathResolver()
    result = resolver.d_merged(domain="teams", filename="result.json")
    assert result == Path("layers/0_layer/teams/D_merge/result.json")


# _normalize_domain errors
def test_normalize_domain_raises_for_empty_string() -> None:
    with pytest.raises(ValueError, match="Domain cannot be empty"):
        _normalize_domain("")


def test_normalize_domain_raises_for_whitespace_only() -> None:
    with pytest.raises(ValueError, match="Domain cannot be empty"):
        _normalize_domain("   ")


def test_normalize_domain_raises_for_path_with_slash() -> None:
    with pytest.raises(ValueError, match="single path segment"):
        _normalize_domain("foo/bar")


def test_normalize_domain_strips_backslash_to_slash_then_rejects() -> None:
    with pytest.raises(ValueError, match="single path segment"):
        _normalize_domain("foo\\bar")


# _normalize_output_name errors
def test_normalize_output_name_raises_for_empty_string() -> None:
    with pytest.raises(ValueError, match="Output filename cannot be empty"):
        _normalize_output_name("   ")


def test_normalize_output_name_raises_for_duplicated_extension() -> None:
    with pytest.raises(ValueError, match="duplicated extension"):
        _normalize_output_name("file.json.json")


# _normalize_relative_parts errors
def test_normalize_relative_parts_raises_when_no_parts_given() -> None:
    with pytest.raises(ValueError, match="At least one output path segment"):
        _normalize_relative_parts()


def test_normalize_relative_parts_raises_for_empty_segment() -> None:
    with pytest.raises(ValueError, match="segment cannot be empty"):
        _normalize_relative_parts("good", "   ")


def test_normalize_relative_parts_raises_for_absolute_path() -> None:
    with pytest.raises(ValueError, match="must stay relative"):
        _normalize_relative_parts("/absolute/path")


def test_normalize_relative_parts_raises_for_dotdot() -> None:
    with pytest.raises(ValueError, match="must stay relative"):
        _normalize_relative_parts("../escape")
