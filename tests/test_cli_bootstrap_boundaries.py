from __future__ import annotations

from pathlib import Path

SCRAPERS_DIR = Path("scrapers")

ALLOWED_MAIN_FILES = {
    "scrapers/cli.py",
    "scrapers/circuits/complete_scraper.py",
    "scrapers/circuits/list_scraper.py",
    "scrapers/constructors/complete_scraper.py",
    "scrapers/constructors/current_constructors_list.py",
    "scrapers/constructors/former_constructors_list.py",
    "scrapers/constructors/indianapolis_only_constructors_list.py",
    "scrapers/constructors/privateer_teams_list.py",
    "scrapers/drivers/complete_scraper.py",
    "scrapers/drivers/fatalities_list_scraper.py",
    "scrapers/drivers/female_drivers_list.py",
    "scrapers/drivers/list_scraper.py",
    "scrapers/engines/complete_scraper.py",
    "scrapers/engines/engine_manufacturers_list.py",
    "scrapers/engines/engine_regulation.py",
    "scrapers/engines/engine_restrictions.py",
    "scrapers/engines/indianapolis_only_engine_manufacturers_list.py",
    "scrapers/grands_prix/complete_scraper.py",
    "scrapers/grands_prix/list_scraper.py",
    "scrapers/grands_prix/red_flagged_races_scraper/world_championship.py",
    "scrapers/points/points_scoring_systems_history.py",
    "scrapers/points/shortened_race_points.py",
    "scrapers/points/sprint_qualifying_points.py",
    "scrapers/seasons/complete_scraper.py",
    "scrapers/seasons/list_scraper.py",
    "scrapers/sponsorship_liveries/scraper.py",
    "scrapers/tyres/list_scraper.py",
}


IDE_ENTRYPOINT_FILES = {
    "scrapers/circuits/entrypoint.py",
    "scrapers/constructors/entrypoint.py",
    "scrapers/drivers/entrypoint.py",
    "scrapers/grands_prix/entrypoint.py",
    "scrapers/seasons/entrypoint.py",
}


def test_no_new_standalone_cli_bootstraps_outside_allowlist() -> None:
    files_with_main: list[str] = []
    for file_path in sorted(SCRAPERS_DIR.rglob("*.py")):
        source = file_path.read_text(encoding="utf-8")
        if 'if __name__ == "__main__":' in source:
            files_with_main.append(str(file_path))

    assert set(files_with_main) == ALLOWED_MAIN_FILES


def test_legacy_wrappers_remain_thin_and_parser_free() -> None:
    for file_path in sorted(ALLOWED_MAIN_FILES):
        if file_path == "scrapers/cli.py":
            continue
        source = Path(file_path).read_text(encoding="utf-8")
        assert "run_deprecated_entrypoint(" in source
        assert "argparse.ArgumentParser(" not in source


def test_ide_entrypoints_stay_function_based_without_cli_bootstrap() -> None:
    for file_path in sorted(IDE_ENTRYPOINT_FILES):
        source = Path(file_path).read_text(encoding="utf-8")
        assert "run_list_scraper" not in source
        assert "install_domain_entrypoint(" in source
        assert 'if __name__ == "__main__":' not in source
        assert "argparse" not in source
