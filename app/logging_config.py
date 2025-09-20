from __future__ import annotations

import logging
from pathlib import Path
from typing import Optional

import structlog


def configure_logging(json_logs: bool = False, level: str = "INFO", log_file: Optional[Path] = None) -> None:
    handlers: list[logging.Handler] = []
    if log_file is not None:
        log_file.parent.mkdir(parents=True, exist_ok=True)
        handlers.append(logging.FileHandler(str(log_file), encoding="utf-8"))
    else:
        handlers.append(logging.StreamHandler())

    logging.basicConfig(level=getattr(logging, level.upper(), logging.INFO), handlers=handlers, force=True)

    processors = [
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso", key="ts"),
    ]
    if json_logs:
        processors.append(structlog.processors.JSONRenderer())
    else:
        # Console renderer is handy for local runs; JSON goes to files when enabled
        processors.append(structlog.dev.ConsoleRenderer())
    structlog.configure(
        processors=processors,
        wrapper_class=structlog.make_filtering_bound_logger(getattr(logging, level.upper(), logging.INFO)),
        cache_logger_on_first_use=True,
    )
