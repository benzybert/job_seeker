from __future__ import annotations

import sys
from loguru import logger


def setup_logging(service_name: str) -> None:
    logger.remove()
    logger.add(
        sys.stdout,
        level="INFO",
        backtrace=False,
        diagnose=False,
        serialize=True,  # JSON logs
        enqueue=True,
    )
    logger.bind(service=service_name)


