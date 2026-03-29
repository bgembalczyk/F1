from scripts import check_known_module_typos as module


def test_validate_target_packages_for_single_rule(tmp_path, monkeypatch):
    package = tmp_path / "sample_package"
    package.mkdir()
    (package / "constants.py").write_text("# ok\n", encoding="utf-8")

    single_rule = module.TypoRule(
        target_packages=(package,),
        expected_module_name="constants.py",
        disallowed_typo_name="contants.py",
        disallowed_import="sample.contants",
    )

    monkeypatch.setattr(module, "TYPO_RULES", (single_rule,))

    assert module._validate_target_packages() == []
