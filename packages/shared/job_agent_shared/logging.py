from __future__ import annotations

import sys
from loguru import logger


def setup_logging(service_name: str) -> None:
    """
    Configure Loguru to emit structured JSON logs to stdout and bind service name.
    """
    logger.remove()
    logger.add(
        sys.stdout,
        level="INFO",
        backtrace=False,
        diagnose=False,
        serialize=True,
         enqueue=True,
    )
    logger.bind(service=service_name)



