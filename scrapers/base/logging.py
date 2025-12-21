from __future__ import annotations

import logging
from typing import Union

LOGGER_NAME = "f1.scrapers"

logger = logging.getLogger(LOGGER_NAME)


def configure_logging(level: Union[int, str] = logging.INFO) -> None:
    if isinstance(level, str):
        level = logging.getLevelName(level.upper())
        if not isinstance(level, int):
            level = logging.INFO

    logging.basicConfig(level=level, format="%(message)s")
    logger.setLevel(level)
