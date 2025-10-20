#!/usr/bin/env python3
"""
Custom exception classes and error handling utilities.
"""

from __future__ import annotations

import time
import logging
from typing import Callable, TypeVar, Any, Optional
from functools import wraps


# Custom exception hierarchy
class PipelineError(Exception):
    """Base exception for all pipeline errors."""
    pass


class ConfigurationError(PipelineError):
    """Raised when configuration is invalid."""
    pass


class ValidationError(PipelineError):
    """Raised when validation fails."""
    pass


class TranscriptionError(PipelineError):
    """Raised when transcription fails."""
    pass


class AnalysisError(PipelineError):
    """Raised when transcript analysis fails."""
    pass


class VideoProcessingError(PipelineError):
    """Raised when video processing fails."""
    pass


class SubtitleGenerationError(PipelineError):
    """Raised when subtitle generation fails."""
    pass


class DependencyError(PipelineError):
    """Raised when required dependency is missing."""
    pass


# Type variable for generic return types
T = TypeVar('T')


def handle_errors(
    logger: Optional[logging.Logger] = None,
    reraise: bool = True,
    default_return: Any = None
) -> Callable:
    """
    Decorator for handling and logging errors.

    Args:
        logger: Logger instance for error logging
        reraise: If True, re-raise the exception after logging
        default_return: Value to return if exception is caught and not re-raised

    Returns:
        Decorated function
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> T:
            try:
                return func(*args, **kwargs)
            except Exception as e:
                if logger:
                    logger.error(f"Error in {func.__name__}: {str(e)}", exc_info=True)

                if reraise:
                    raise
                return default_return

        return wrapper
    return decorator


def retry_on_failure(
    max_retries: int = 3,
    delay: float = 1.0,
    exponential_backoff: bool = True,
    exceptions: tuple = (Exception,),
    logger: Optional[logging.Logger] = None
) -> Callable:
    """
    Decorator for retrying function calls on failure.

    Args:
        max_retries: Maximum number of retry attempts
        delay: Initial delay between retries in seconds
        exponential_backoff: If True, double delay after each retry
        exceptions: Tuple of exception types to catch and retry
        logger: Logger instance for retry logging

    Returns:
        Decorated function
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> T:
            current_delay = delay
            last_exception = None

            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e

                    if attempt < max_retries:
                        if logger:
                            logger.warning(
                                f"Attempt {attempt + 1}/{max_retries + 1} failed for {func.__name__}: {str(e)}. "
                                f"Retrying in {current_delay:.1f}s..."
                            )
                        time.sleep(current_delay)

                        if exponential_backoff:
                            current_delay *= 2
                    else:
                        if logger:
                            logger.error(
                                f"All {max_retries + 1} attempts failed for {func.__name__}: {str(e)}"
                            )
                        raise last_exception

            # This should never be reached, but satisfies type checker
            raise last_exception

        return wrapper
    return decorator


class ErrorContext:
    """
    Context manager for handling errors with cleanup.

    Example:
        with ErrorContext("processing video", logger) as ctx:
            # Do something that might fail
            ctx.add_cleanup(lambda: cleanup_temp_files())
    """

    def __init__(self, operation: str, logger: Optional[logging.Logger] = None):
        """
        Initialize error context.

        Args:
            operation: Description of the operation being performed
            logger: Logger instance for error logging
        """
        self.operation = operation
        self.logger = logger
        self.cleanup_functions: list[Callable] = []
        self.error: Optional[Exception] = None

    def add_cleanup(self, cleanup_func: Callable) -> None:
        """Add a cleanup function to be called on exit."""
        self.cleanup_functions.append(cleanup_func)

    def __enter__(self) -> ErrorContext:
        """Enter the context."""
        if self.logger:
            self.logger.debug(f"Starting operation: {self.operation}")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit the context, running cleanup functions."""
        if exc_type is not None:
            self.error = exc_val
            if self.logger:
                self.logger.error(
                    f"Error during {self.operation}: {str(exc_val)}",
                    exc_info=True
                )

        # Run cleanup functions
        for cleanup_func in reversed(self.cleanup_functions):
            try:
                cleanup_func()
            except Exception as e:
                if self.logger:
                    self.logger.warning(f"Cleanup function failed: {str(e)}")

        # Don't suppress the original exception
        return False


def format_error_message(error: Exception, context: Optional[str] = None) -> str:
    """
    Format error message with context.

    Args:
        error: Exception instance
        context: Optional context description

    Returns:
        Formatted error message
    """
    error_type = type(error).__name__
    error_msg = str(error)

    if context:
        return f"{context}: {error_type} - {error_msg}"
    return f"{error_type}: {error_msg}"


def validate_dependency(
    dependency_name: str,
    check_function: Callable[[], bool],
    install_instructions: str
) -> None:
    """
    Validate that a required dependency is available.

    Args:
        dependency_name: Name of the dependency
        check_function: Function that returns True if dependency is available
        install_instructions: Instructions for installing the dependency

    Raises:
        DependencyError: If dependency is not available
    """
    if not check_function():
        raise DependencyError(
            f"Required dependency '{dependency_name}' is not available.\n"
            f"Install instructions: {install_instructions}"
        )
