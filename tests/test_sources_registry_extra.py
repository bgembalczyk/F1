# ruff: noqa: E501, PLR2004
"""Tests for sources_registry covering uncovered lines."""

import warnings

import pytest

from scrapers.wiki import sources_registry as registry


class TestWikiSourceDefinitionProperties:
    def test_output_category_alias(self):
        source = registry.WikiSourceDefinition(
            domain="drivers",
            seed_name="drivers",
            source_name="drivers",
            output_file="f1_drivers.json",
        )
        assert source.output_category == "drivers"

    def test_list_filename_alias(self):
        source = registry.WikiSourceDefinition(
            domain="drivers",
            seed_name="drivers",
            source_name="drivers",
            output_file="f1_drivers.json",
        )
        assert source.list_filename == "f1_drivers.json"


class TestResolveListFilename:
    def test_legacy_filename_emits_warning(self):
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always", DeprecationWarning)
            result = registry.resolve_list_filename(
                "f1_engine_manufacturers_indianapolis_only.json",
                warn=True,
            )
        assert result == "f1_indianapolis_only_engine_manufacturers.json"
        assert any(item.category is DeprecationWarning for item in caught)

    def test_canonical_filename_passes_through(self):
        result = registry.resolve_list_filename("f1_drivers.json", warn=True)
        assert result == "f1_drivers.json"

    def test_no_warn_does_not_emit(self):
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always", DeprecationWarning)
            result = registry.resolve_list_filename(
                "f1_engine_manufacturers_indianapolis_only.json",
                warn=False,
            )
        assert result == "f1_indianapolis_only_engine_manufacturers.json"
        assert not any(item.category is DeprecationWarning for item in caught)


class TestGetSourceByListFilename:
    def test_resolves_canonical_filename(self):
        source = registry.get_source_by_list_filename("f1_drivers.json", warn=False)
        assert source.seed_name == "drivers"

    def test_raises_key_error_for_unknown_filename(self):
        with pytest.raises(KeyError, match="Unknown wiki source list filename"):
            registry.get_source_by_list_filename("nonexistent_file.json", warn=False)

    def test_resolves_legacy_filename_with_warning(self):
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always", DeprecationWarning)
            source = registry.get_source_by_list_filename(
                "f1_engine_manufacturers_indianapolis_only.json",
                warn=True,
            )
        assert source.seed_name == "engines_indianapolis_only"
        assert any(item.category is DeprecationWarning for item in caught)


class TestGetSourceBySeedName:
    def test_raises_key_error_for_unknown_seed(self):
        with pytest.raises(KeyError, match="Unknown wiki source seed_name"):
            registry.get_source_by_seed_name("nonexistent_seed", warn=False)


class TestGetSourceBySourceName:
    def test_raises_key_error_for_unknown_source_name(self):
        with pytest.raises(KeyError, match="Unknown wiki source source_name"):
            registry.get_source_by_source_name("nonexistent_source_name")


class TestEnsureUniqueOrRaise:
    def test_adds_to_seen_when_not_present(self):
        seen: set[str] = set()
        registry.ensure_unique_or_raise(
            value="drivers",
            seen=seen,
            duplicate_message="dup",
        )
        assert "drivers" in seen

    def test_raises_when_already_present(self):
        seen = {"drivers"}
        with pytest.raises(ValueError, match="dup"):
            registry.ensure_unique_or_raise(
                value="drivers",
                seen=seen,
                duplicate_message="dup",
            )


class TestValidateCanonicalSource:
    def test_raises_for_empty_domain(self):
        source = registry.WikiSourceDefinition(
            domain="",
            seed_name="test_seed",
            source_name="test_source",
            output_file="test.json",
        )
        with pytest.raises(ValueError, match="Empty domain"):
            registry.validate_canonical_source(
                source=source,
                seen_seed_names=set(),
                seen_source_names=set(),
                seen_filenames=set(),
            )

    def test_raises_for_whitespace_domain(self):
        source = registry.WikiSourceDefinition(
            domain="   ",
            seed_name="test_seed",
            source_name="test_source",
            output_file="test.json",
        )
        with pytest.raises(ValueError, match="Empty domain"):
            registry.validate_canonical_source(
                source=source,
                seen_seed_names=set(),
                seen_source_names=set(),
                seen_filenames=set(),
            )

    def test_raises_for_duplicate_seed_name(self):
        source = registry.WikiSourceDefinition(
            domain="drivers",
            seed_name="drivers",
            source_name="drivers_alt",
            output_file="drivers_alt.json",
        )
        with pytest.raises(ValueError, match="Duplicate canonical seed_name"):
            registry.validate_canonical_source(
                source=source,
                seen_seed_names={"drivers"},
                seen_source_names=set(),
                seen_filenames=set(),
            )

    def test_raises_for_duplicate_source_name(self):
        source = registry.WikiSourceDefinition(
            domain="drivers",
            seed_name="drivers_new",
            source_name="drivers_existing",
            output_file="drivers_new.json",
        )
        with pytest.raises(ValueError, match="Duplicate canonical source_name"):
            registry.validate_canonical_source(
                source=source,
                seen_seed_names=set(),
                seen_source_names={"drivers_existing"},
                seen_filenames=set(),
            )

    def test_raises_for_duplicate_output_file(self):
        source = registry.WikiSourceDefinition(
            domain="drivers",
            seed_name="drivers_new",
            source_name="drivers_new",
            output_file="f1_drivers.json",
        )
        with pytest.raises(ValueError, match="Duplicate canonical list_filename"):
            registry.validate_canonical_source(
                source=source,
                seen_seed_names=set(),
                seen_source_names=set(),
                seen_filenames={"f1_drivers.json"},
            )

    def test_raises_when_source_name_conflicts_with_seed_name(self):
        # source_name != seed_name but source_name is already in seen_seed_names
        source = registry.WikiSourceDefinition(
            domain="drivers",
            seed_name="drivers_new",
            source_name="existing_seed",
            output_file="drivers_new.json",
        )
        with pytest.raises(ValueError, match="naming conflict"):
            registry.validate_canonical_source(
                source=source,
                seen_seed_names={"existing_seed"},
                seen_source_names=set(),
                seen_filenames=set(),
            )


class TestValidateLegacySeedAliases:
    def test_raises_when_alias_conflicts_with_canonical_seed(self, monkeypatch):
        import scrapers.wiki.sources_registry as reg

        monkeypatch.setattr(
            reg,
            "LEGACY_SEED_NAME_ALIASES",
            {"drivers": "drivers"},  # "drivers" is in SOURCE_BY_SEED_NAME
        )
        monkeypatch.setattr(
            reg,
            "SOURCE_BY_SEED_NAME",
            {"drivers": object(), "drivers_current": object()},
        )
        with pytest.raises(ValueError, match="Legacy seed alias conflicts"):
            reg.validate_legacy_seed_aliases()

    def test_raises_when_canonical_target_missing(self, monkeypatch):
        import scrapers.wiki.sources_registry as reg

        monkeypatch.setattr(
            reg,
            "LEGACY_SEED_NAME_ALIASES",
            {"old_constructors": "nonexistent_canonical"},
        )
        monkeypatch.setattr(
            reg,
            "SOURCE_BY_SEED_NAME",
            {"drivers": object()},
        )
        with pytest.raises(ValueError, match="Legacy seed alias points to missing"):
            reg.validate_legacy_seed_aliases()


class TestValidateLegacyFilenameAliases:
    def test_raises_when_alias_conflicts_with_canonical_filename(self, monkeypatch):
        import scrapers.wiki.sources_registry as reg

        monkeypatch.setattr(
            reg,
            "LEGACY_LIST_FILENAME_ALIASES",
            {"f1_drivers.json": "f1_drivers_new.json"},
        )
        monkeypatch.setattr(
            reg,
            "SOURCE_BY_LIST_FILENAME",
            {"f1_drivers.json": object(), "f1_drivers_new.json": object()},
        )
        with pytest.raises(ValueError, match="Legacy list filename alias conflicts"):
            reg.validate_legacy_filename_aliases()

    def test_raises_when_canonical_target_missing(self, monkeypatch):
        import scrapers.wiki.sources_registry as reg

        monkeypatch.setattr(
            reg,
            "LEGACY_LIST_FILENAME_ALIASES",
            {"old_file.json": "nonexistent_canonical.json"},
        )
        monkeypatch.setattr(
            reg,
            "SOURCE_BY_LIST_FILENAME",
            {"f1_drivers.json": object()},
        )
        with pytest.raises(ValueError, match="Legacy filename alias points to missing"):
            reg.validate_legacy_filename_aliases()
