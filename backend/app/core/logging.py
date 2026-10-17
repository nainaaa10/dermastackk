"""
Dermastack Centralized Logging Configuration.
Ensures structured, informative logging without leaking secrets or image data.
"""

import logging
import sys


def setup_logging():
    """Configures structured console logging for the application."""
    logging_level = logging.INFO

    formatter = logging.Formatter(
        fmt="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)

    root_logger = logging.getLogger()
    root_logger.setLevel(logging_level)
    # Avoid duplicate handlers if reloaded
    if not root_logger.handlers:
        root_logger.addHandler(handler)
    else:
        root_logger.handlers = [handler]

    # Silence noisy third-party loggers
    logging.getLogger("uvicorn.access").setLevel(logging.INFO)
    logging.getLogger("uvicorn.error").setLevel(logging.INFO)
    logging.getLogger("PIL").setLevel(logging.WARNING)


logger = logging.getLogger("dermastack")
