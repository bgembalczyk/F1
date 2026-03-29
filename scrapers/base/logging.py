import logging

from scrapers.base.constants.runtime import LOGGER_NAME

logger = logging.getLogger(LOGGER_NAME)


def get_logger(scraper_name: str) -> logging.LoggerAdapter:
    base_logger = logging.getLogger(f"{LOGGER_NAME}.{scraper_name}")
    return logging.LoggerAdapter(base_logger, {"scraper": scraper_name})
