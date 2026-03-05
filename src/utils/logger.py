"""
Centralized Logging Configuration
Uses Rich for beautiful console output and file logging for persistence.
"""

import os
import logging
from datetime import datetime
from rich.logging import RichHandler


def setup_logger(
    name: str = "epassport_agent",
    level: int = logging.INFO,
    log_to_file: bool = True,
) -> logging.Logger:
    """
    Set up a configured logger with both console (Rich) and file handlers.

    Args:
        name: Logger name
        level: Logging level
        log_to_file: Whether to also log to a file

    Returns:
        Configured Logger instance
    """
    logger = logging.getLogger(name)

    # Avoid adding duplicate handlers
    if logger.handlers:
        return logger

    logger.setLevel(level)

    # ── Rich Console Handler ──────────────────────────────────
    console_handler = RichHandler(
        level=level,
        rich_tracebacks=True,
        tracebacks_show_locals=True,
        markup=True,
        show_time=True,
        show_path=False,
    )
    console_format = logging.Formatter("%(message)s")
    console_handler.setFormatter(console_format)
    logger.addHandler(console_handler)

    # ── File Handler ──────────────────────────────────────────
    if log_to_file:
        log_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "logs")
        os.makedirs(log_dir, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d")
        log_file = os.path.join(log_dir, f"epassport_agent_{timestamp}.log")

        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setLevel(level)
        file_format = logging.Formatter(
            "%(asctime)s | %(name)s | %(levelname)s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        file_handler.setFormatter(file_format)
        logger.addHandler(file_handler)

    return logger
