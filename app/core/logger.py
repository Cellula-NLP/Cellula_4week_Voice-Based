# app/core/logger.py
"""Centralized logging configuration."""
import logging
import sys


def setup_logger() -> None:
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    # Avoid duplicate handlers if this is called multiple times
    if logger.hasHandlers():
        return

    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.INFO)

    formatter = logging.Formatter(
        "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    # Silence noisy libraries
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("faster_whisper").setLevel(logging.WARNING)