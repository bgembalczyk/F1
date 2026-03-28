from typing import Any


def run_list_scraper(*args: Any, **kwargs: Any):
    from scrapers.drivers.entrypoint import run_list_scraper as _run_list_scraper

    return _run_list_scraper(*args, **kwargs)


__all__ = ["run_list_scraper"]
