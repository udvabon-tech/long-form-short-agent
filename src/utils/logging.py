#!/usr/bin/env python3
"""
Enhanced logging utilities with structured output and file rotation.
"""

from __future__ import annotations

import logging
import sys
from pathlib import Path
from logging.handlers import RotatingFileHandler
from typing import Optional
from datetime import datetime


# ANSI color codes for terminal output
class Colors:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    MAGENTA = "\033[95m"
    CYAN = "\033[96m"
    WHITE = "\033[97m"
    GRAY = "\033[90m"


class ColoredFormatter(logging.Formatter):
    """Custom formatter with color support for console output."""

    LEVEL_COLORS = {
        logging.DEBUG: Colors.GRAY,
        logging.INFO: Colors.BLUE,
        logging.WARNING: Colors.YELLOW,
        logging.ERROR: Colors.RED,
        logging.CRITICAL: Colors.RED + Colors.BOLD,
    }

    LEVEL_ICONS = {
        logging.DEBUG: "🔍",
        logging.INFO: "ℹ️ ",
        logging.WARNING: "⚠️ ",
        logging.ERROR: "❌",
        logging.CRITICAL: "🚨",
    }

    def __init__(self, use_colors: bool = True):
        super().__init__()
        self.use_colors = use_colors

    def format(self, record: logging.LogRecord) -> str:
        """Format log record with colors and icons."""
        if not self.use_colors:
            return f"[{record.levelname}] {record.getMessage()}"

        color = self.LEVEL_COLORS.get(record.levelno, Colors.WHITE)
        icon = self.LEVEL_ICONS.get(record.levelno, "•")
        level_name = record.levelname

        # Format timestamp
        timestamp = datetime.fromtimestamp(record.created).strftime("%H:%M:%S")

        # Build message
        message = record.getMessage()

        # Add module info for debug level
        if record.levelno == logging.DEBUG:
            module_info = f"{Colors.GRAY}[{record.name}]{Colors.RESET} "
        else:
            module_info = ""

        return f"{Colors.GRAY}{timestamp}{Colors.RESET} {icon} {color}{level_name:8s}{Colors.RESET} {module_info}{message}"


class FileFormatter(logging.Formatter):
    """Formatter for file output (no colors)."""

    def __init__(self):
        super().__init__(
            fmt="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )


def setup_logging(
    log_level: str = "INFO",
    log_dir: Optional[Path] = None,
    log_to_file: bool = True,
    log_to_console: bool = True,
    max_file_size: int = 10 * 1024 * 1024,  # 10 MB
    backup_count: int = 5
) -> logging.Logger:
    """
    Set up logging configuration for the entire application.

    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_dir: Directory for log files (defaults to ./logs)
        log_to_file: Enable file logging
        log_to_console: Enable console logging
        max_file_size: Maximum size of log file before rotation
        backup_count: Number of backup log files to keep

    Returns:
        Configured root logger
    """
    # Get numeric level
    numeric_level = getattr(logging, log_level.upper(), logging.INFO)

    # Get root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(numeric_level)

    # Remove existing handlers
    root_logger.handlers.clear()

    # Console handler with colors
    if log_to_console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(numeric_level)
        console_handler.setFormatter(ColoredFormatter(use_colors=True))
        root_logger.addHandler(console_handler)

    # File handler with rotation
    if log_to_file:
        if log_dir is None:
            log_dir = Path("logs")

        log_dir.mkdir(parents=True, exist_ok=True)

        # Main log file
        log_file = log_dir / "pipeline.log"
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=max_file_size,
            backupCount=backup_count,
            encoding='utf-8'
        )
        file_handler.setLevel(numeric_level)
        file_handler.setFormatter(FileFormatter())
        root_logger.addHandler(file_handler)

        # Error log file (only ERROR and CRITICAL)
        error_log_file = log_dir / "errors.log"
        error_handler = RotatingFileHandler(
            error_log_file,
            maxBytes=max_file_size,
            backupCount=backup_count,
            encoding='utf-8'
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(FileFormatter())
        root_logger.addHandler(error_handler)

    return root_logger


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance for a specific module.

    Args:
        name: Logger name (usually __name__)

    Returns:
        Logger instance
    """
    return logging.getLogger(name)


def log_stage_start(logger: logging.Logger, stage_name: str) -> None:
    """Log the start of a pipeline stage."""
    logger.info(f"{Colors.CYAN}{'='*60}{Colors.RESET}")
    logger.info(f"{Colors.CYAN}Starting stage: {Colors.BOLD}{stage_name}{Colors.RESET}")
    logger.info(f"{Colors.CYAN}{'='*60}{Colors.RESET}")


def log_stage_complete(logger: logging.Logger, stage_name: str, duration: float) -> None:
    """Log the completion of a pipeline stage."""
    logger.info(f"{Colors.GREEN}✓ Stage completed: {stage_name} ({duration:.2f}s){Colors.RESET}")


def log_stage_error(logger: logging.Logger, stage_name: str, error: Exception) -> None:
    """Log a stage error."""
    logger.error(f"{Colors.RED}✗ Stage failed: {stage_name}{Colors.RESET}")
    logger.error(f"{Colors.RED}Error: {str(error)}{Colors.RESET}")


def log_progress(logger: logging.Logger, current: int, total: int, message: str = "") -> None:
    """Log progress information."""
    percentage = (current / total * 100) if total > 0 else 0
    progress_bar = "█" * int(percentage / 5) + "░" * (20 - int(percentage / 5))
    logger.info(f"Progress: [{progress_bar}] {percentage:.1f}% ({current}/{total}) {message}")
