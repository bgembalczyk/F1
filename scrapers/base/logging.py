import logging

LOGGER_NAME = "f1.scrapers"

logger = logging.getLogger(LOGGER_NAME)


def get_logger(scraper_name: str) -> logging.LoggerAdapter:
    base_logger = logging.getLogger(f"{LOGGER_NAME}.{scraper_name}")
    return logging.LoggerAdapter(base_logger, {"scraper": scraper_name})


def configure_logging(level: int | str = logging.INFO) -> None:
    if isinstance(level, str):
        level = logging.getLevelName(level.upper())
        if not isinstance(level, int):
            level = logging.INFO

    logging.basicConfig(level=level, format="%(message)s")
    logger.setLevel(level)
