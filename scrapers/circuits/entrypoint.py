"""Domain facade for launching the circuits list scraper."""

from scrapers.base.domain_entrypoint import build_run_list_scraper_for_domain
from scrapers.base.domain_entrypoint import get_domain_entrypoint_config

_DOMAIN = "circuits"
run_list_scraper = build_run_list_scraper_for_domain(_DOMAIN)


def __getattr__(name: str):
    exported_names = {
        "ENTRYPOINT_CONFIG",
        "LIST_SCRAPER_CLASS",
        "DEFAULT_OUTPUT_JSON",
        "DEFAULT_OUTPUT_CSV",
        "RUN_CONFIG_PROFILE",
    }
    if name not in exported_names:
        msg = f"module {__name__!r} has no attribute {name!r}"
        raise AttributeError(msg)

    config = get_domain_entrypoint_config(_DOMAIN)
    aliases = {
        "ENTRYPOINT_CONFIG": config,
        "LIST_SCRAPER_CLASS": config.list_scraper_cls,
        "DEFAULT_OUTPUT_JSON": config.default_output_json,
        "DEFAULT_OUTPUT_CSV": config.default_output_csv,
        "RUN_CONFIG_PROFILE": config.run_config_profile,
    }
    return aliases[name]
