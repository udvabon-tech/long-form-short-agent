#!/usr/bin/env python3
"""
Base agent class for all pipeline agents.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Optional, Dict
from pathlib import Path
import logging

from ..config.schemas import ProjectConfig, PipelineState, StageMetrics
from ..config.settings import Settings
from ..utils.errors import PipelineError
from ..utils.metrics import MetricsCollector


@dataclass
class AgentResult:
    """Result from an agent execution."""
    success: bool
    message: str
    artifacts: Dict[str, Path] = None
    metadata: Dict[str, Any] = None
    error: Optional[Exception] = None

    def __post_init__(self):
        if self.artifacts is None:
            self.artifacts = {}
        if self.metadata is None:
            self.metadata = {}


class BaseAgent(ABC):
    """
    Base class for all pipeline agents.

    Each agent is responsible for a specific stage of the pipeline and
    operates autonomously within its domain.
    """

    def __init__(
        self,
        settings: Settings,
        project_config: ProjectConfig,
        metrics_collector: MetricsCollector,
        logger: Optional[logging.Logger] = None
    ):
        """
        Initialize base agent.

        Args:
            settings: Global settings
            project_config: Project configuration
            metrics_collector: Metrics collector for performance tracking
            logger: Logger instance
        """
        self.settings = settings
        self.project_config = project_config
        self.metrics = metrics_collector
        self.logger = logger or logging.getLogger(self.__class__.__name__)

    @property
    @abstractmethod
    def stage_name(self) -> str:
        """Return the name of this agent's stage."""
        pass

    @abstractmethod
    def validate_preconditions(self) -> None:
        """
        Validate that all preconditions for this stage are met.

        Raises:
            PipelineError: If preconditions are not met
        """
        pass

    @abstractmethod
    def execute(self) -> AgentResult:
        """
        Execute the agent's primary task.

        Returns:
            AgentResult with execution status and artifacts
        """
        pass

    @abstractmethod
    def validate_postconditions(self, result: AgentResult) -> None:
        """
        Validate that the agent's output meets expected criteria.

        Args:
            result: The result from execute()

        Raises:
            PipelineError: If postconditions are not met
        """
        pass

    def run(self) -> AgentResult:
        """
        Execute the complete agent workflow with validation.

        Returns:
            AgentResult with execution status

        Raises:
            PipelineError: If any stage fails
        """
        self.logger.info(f"Starting agent: {self.stage_name}")

        try:
            # Validate preconditions
            self.logger.debug("Validating preconditions...")
            self.validate_preconditions()

            # Execute main task
            self.logger.debug("Executing main task...")
            result = self.execute()

            # Validate postconditions
            if result.success:
                self.logger.debug("Validating postconditions...")
                self.validate_postconditions(result)

            if result.success:
                self.logger.info(f"✓ Agent completed successfully: {self.stage_name}")
            else:
                self.logger.error(f"✗ Agent failed: {self.stage_name}")
                if result.error:
                    self.logger.error(f"Error: {result.error}")

            return result

        except Exception as e:
            self.logger.error(f"Agent {self.stage_name} failed with exception: {str(e)}", exc_info=True)
            return AgentResult(
                success=False,
                message=f"Agent failed: {str(e)}",
                error=e
            )

    def _ensure_directory(self, path: Path) -> None:
        """Ensure a directory exists."""
        path.mkdir(parents=True, exist_ok=True)
        self.logger.debug(f"Ensured directory exists: {path}")

    def _check_file_exists(self, path: Path, description: str = "file") -> None:
        """
        Check that a required file exists.

        Args:
            path: Path to check
            description: Description of the file

        Raises:
            PipelineError: If file doesn't exist
        """
        if not path.exists():
            raise PipelineError(f"Required {description} not found: {path}")
        if not path.is_file():
            raise PipelineError(f"Path is not a file: {path}")
        self.logger.debug(f"Verified {description} exists: {path}")

    def _check_file_not_empty(self, path: Path, min_size_bytes: int = 1) -> None:
        """
        Check that a file is not empty.

        Args:
            path: Path to check
            min_size_bytes: Minimum required file size

        Raises:
            PipelineError: If file is too small
        """
        size = path.stat().st_size
        if size < min_size_bytes:
            raise PipelineError(
                f"File is too small ({size} bytes, minimum {min_size_bytes}): {path}"
            )
        self.logger.debug(f"Verified file size: {path} ({size:,} bytes)")
