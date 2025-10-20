#!/usr/bin/env python3
"""
Master orchestrator for coordinating all pipeline agents.

This is the brain of the agentic system, responsible for:
- Initializing all agents
- Managing pipeline execution flow
- Handling errors and retries
- Coordinating state management
- Collecting and reporting metrics
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import List, Optional, Dict, Any
from datetime import datetime

from ..config.settings import Settings, load_settings
from ..config.schemas import ProjectConfig, PipelineState, PipelineStage, StageMetrics, StageStatus
from ..config.validators import (
    validate_project_structure,
    validate_ffmpeg_installation,
    validate_dependencies
)
from ..utils.logging import setup_logging, get_logger, log_stage_start, log_stage_complete, log_stage_error
from ..utils.errors import PipelineError, ConfigurationError, DependencyError, ErrorContext
from ..utils.metrics import MetricsCollector
from .base_agent import BaseAgent, AgentResult


class PipelineOrchestrator:
    """
    Master orchestrator for the reel generation pipeline.

    Coordinates all agents and manages the complete end-to-end workflow
    from source video to final reels.
    """

    def __init__(
        self,
        project_config: ProjectConfig,
        settings: Optional[Settings] = None,
        resume_from_checkpoint: bool = False
    ):
        """
        Initialize the pipeline orchestrator.

        Args:
            project_config: Project configuration
            settings: Global settings (loads from config.yaml if None)
            resume_from_checkpoint: If True, attempt to resume from saved state
        """
        # Load settings
        self.settings = settings or load_settings()

        # Setup logging
        self.logger = setup_logging(
            log_level=self.settings.system.log_level,
            log_dir=project_config.project_root / self.settings.system.log_dir
        )
        self.logger = get_logger(__name__)

        self.logger.info(f"Initializing Pipeline Orchestrator for project: {project_config.project_name}")

        # Store configuration
        self.project_config = project_config

        # Initialize metrics collection
        self.metrics = MetricsCollector()

        # Initialize pipeline state
        checkpoint_path = project_config.project_root / "Logs" / "pipeline_state.json"
        if resume_from_checkpoint and checkpoint_path.exists():
            self.logger.info(f"Resuming from checkpoint: {checkpoint_path}")
            self.state = PipelineState.load_checkpoint(project_config, checkpoint_path)
        else:
            self.state = PipelineState(project_config=project_config)

        # Agent registry (will be populated by initialize_agents)
        self.agents: Dict[str, BaseAgent] = {}

        # Validation
        self._validate_system()

    def _validate_system(self) -> None:
        """Validate system requirements and dependencies."""
        self.logger.info("Validating system requirements...")

        # Validate dependencies
        deps = validate_dependencies()
        missing_deps = [name for name, available in deps.items() if not available]

        if missing_deps:
            raise DependencyError(
                f"Missing required dependencies: {', '.join(missing_deps)}\n"
                "Please install missing dependencies before proceeding."
            )

        # Validate FFmpeg
        try:
            ffmpeg_info = validate_ffmpeg_installation()
            self.logger.info(f"FFmpeg validated: {ffmpeg_info['version']}")
        except Exception as e:
            raise DependencyError(f"FFmpeg validation failed: {str(e)}")

        # Validate project structure
        messages = validate_project_structure(
            self.project_config.project_root,
            create_missing=True
        )
        for msg in messages:
            self.logger.info(msg)

        # Validate API key
        if not self.settings.api.gemini_api_key:
            raise ConfigurationError(
                "GEMINI_API_KEY environment variable is not set.\n"
                "Export it in your shell: export GEMINI_API_KEY=\"your-key-here\""
            )

        self.logger.info("✓ System validation complete")

    def initialize_agents(self) -> None:
        """Initialize all pipeline agents."""
        self.logger.info("Initializing pipeline agents...")

        # Import agents here to avoid circular dependencies
        from .audio_extraction_agent import AudioExtractionAgent
        from .transcription_agent import TranscriptionAgent
        from .analysis_agent import AnalysisAgent
        from .video_processing_agent import VideoProcessingAgent
        from .subtitle_agent import SubtitleAgent
        from .finalization_agent import FinalizationAgent

        # Create agent instances
        agent_classes = [
            AudioExtractionAgent,
            TranscriptionAgent,
            AnalysisAgent,
            VideoProcessingAgent,
            SubtitleAgent,
            FinalizationAgent
        ]

        for agent_class in agent_classes:
            agent = agent_class(
                settings=self.settings,
                project_config=self.project_config,
                metrics_collector=self.metrics,
                logger=get_logger(agent_class.__name__)
            )
            self.agents[agent.stage_name] = agent
            self.logger.debug(f"Initialized agent: {agent.stage_name}")

        self.logger.info(f"✓ Initialized {len(self.agents)} agents")

    def execute_stage(self, stage_name: str) -> AgentResult:
        """
        Execute a single pipeline stage.

        Args:
            stage_name: Name of the stage to execute

        Returns:
            AgentResult from the stage execution
        """
        agent = self.agents.get(stage_name)
        if not agent:
            raise PipelineError(f"Unknown stage: {stage_name}")

        # Create stage metric
        stage_metric = self.state.add_stage_metric(stage_name)
        stage_metric.start()

        log_stage_start(self.logger, stage_name)

        with ErrorContext(f"executing stage {stage_name}", self.logger) as ctx:
            try:
                # Execute agent
                with self.metrics.time_stage(stage_name):
                    result = agent.run()

                # Update metrics
                if result.success:
                    stage_metric.complete()
                    stage_metric.artifacts = {
                        k: str(v) for k, v in result.artifacts.items()
                    }
                    log_stage_complete(self.logger, stage_name, stage_metric.duration_seconds)
                else:
                    error_msg = result.error or result.message
                    stage_metric.fail(str(error_msg))
                    log_stage_error(self.logger, stage_name, result.error or Exception(result.message))

                    # Handle retry logic
                    if self.settings.error_handling.max_retries > stage_metric.retries:
                        stage_metric.retries += 1
                        self.logger.warning(
                            f"Retrying stage {stage_name} "
                            f"(attempt {stage_metric.retries}/{self.settings.error_handling.max_retries})"
                        )
                        # Recursive retry
                        return self.execute_stage(stage_name)

                # Save checkpoint after each stage
                if self.settings.error_handling.save_checkpoints:
                    self.state.save_checkpoint()

                return result

            except Exception as e:
                stage_metric.fail(str(e))
                log_stage_error(self.logger, stage_name, e)

                if not self.settings.error_handling.continue_on_error:
                    raise

                return AgentResult(
                    success=False,
                    message=f"Stage failed: {str(e)}",
                    error=e
                )

    def execute_pipeline(self) -> bool:
        """
        Execute the complete pipeline.

        Returns:
            True if pipeline completed successfully, False otherwise
        """
        self.logger.info("=" * 70)
        self.logger.info(f"🚀 Starting Pipeline: {self.project_config.project_name}")
        self.logger.info("=" * 70)

        try:
            # Initialize agents if not already done
            if not self.agents:
                self.initialize_agents()

            # Execute stages in order
            for stage_name in self.settings.pipeline.stages:
                self.logger.info(f"\n{'='*70}")
                self.logger.info(f"Stage: {stage_name}")
                self.logger.info(f"{'='*70}\n")

                # Execute stage
                result = self.execute_stage(stage_name)

                if not result.success:
                    error_msg = f"Pipeline failed at stage: {stage_name}"
                    self.logger.error(error_msg)
                    self.state.complete(success=False)
                    self.state.error_message = error_msg
                    return False

            # Pipeline completed successfully
            self.logger.info("\n" + "=" * 70)
            self.logger.info("✨ Pipeline Completed Successfully!")
            self.logger.info("=" * 70)

            self.state.complete(success=True)
            return True

        except Exception as e:
            self.logger.error(f"Pipeline failed with exception: {str(e)}", exc_info=True)
            self.state.complete(success=False)
            self.state.error_message = str(e)
            return False

        finally:
            # Complete metrics collection
            self.metrics.complete()

            # Save final state
            self.state.save_checkpoint()

            # Export metrics
            if self.settings.monitoring.export_metrics:
                metrics_path = self.project_config.project_root / "Logs" / self.settings.monitoring.metrics_file
                self.metrics.export_to_file(metrics_path)
                self.logger.info(f"Metrics exported to: {metrics_path}")

            # Print summary
            self._print_summary()

    def _print_summary(self) -> None:
        """Print execution summary."""
        self.logger.info("\n" + "=" * 70)
        self.logger.info("EXECUTION SUMMARY")
        self.logger.info("=" * 70)

        # Project info
        self.logger.info(f"\nProject: {self.project_config.project_name}")
        self.logger.info(f"Location: {self.project_config.project_root}")

        # Status
        status = "✓ SUCCESS" if self.state.success else "✗ FAILED"
        self.logger.info(f"\nStatus: {status}")

        # Timing
        self.logger.info(f"Started: {self.state.started_at.strftime('%Y-%m-%d %H:%M:%S')}")
        if self.state.completed_at:
            self.logger.info(f"Completed: {self.state.completed_at.strftime('%Y-%m-%d %H:%M:%S')}")
            self.logger.info(f"Duration: {self.state.total_duration_seconds:.2f}s")

        # Reels
        self.logger.info(f"\nReels Generated: {len(self.project_config.reels)}")

        # Stage summary
        self.logger.info("\nStage Results:")
        for metric in self.state.stage_metrics:
            status_icon = "✓" if metric.status == StageStatus.COMPLETED else "✗"
            self.logger.info(
                f"  {status_icon} {metric.stage:30s} {metric.duration_seconds:8.2f}s"
            )
            if metric.error_message:
                self.logger.info(f"     Error: {metric.error_message}")

        # Output location
        if self.state.success:
            output_dir = self.project_config.project_root / "Output"
            self.logger.info(f"\n📁 Final reels available at: {output_dir}/")

        self.logger.info("\n" + "=" * 70 + "\n")

        # Print detailed metrics
        if self.settings.monitoring.enabled:
            self.metrics.print_summary()

    def get_status(self) -> Dict[str, Any]:
        """
        Get current pipeline status.

        Returns:
            Dictionary with status information
        """
        return {
            "project_name": self.project_config.project_name,
            "current_stage": self.state.current_stage.value,
            "success": self.state.success,
            "started_at": self.state.started_at.isoformat(),
            "completed_at": self.state.completed_at.isoformat() if self.state.completed_at else None,
            "duration_seconds": self.state.total_duration_seconds,
            "stages": [
                {
                    "name": m.stage,
                    "status": m.status.value,
                    "duration": m.duration_seconds
                }
                for m in self.state.stage_metrics
            ],
            "reels": len(self.project_config.reels),
            "error": self.state.error_message
        }


def create_orchestrator(
    project_name: str,
    source_video: Path,
    project_root: Optional[Path] = None
) -> PipelineOrchestrator:
    """
    Factory function to create a pipeline orchestrator.

    Args:
        project_name: Name of the project
        source_video: Path to source video file
        project_root: Root directory for the project (creates if None)

    Returns:
        Configured PipelineOrchestrator instance
    """
    # Create project root if not specified
    if project_root is None:
        project_root = Path("Projects") / project_name

    # Create project configuration
    project_config = ProjectConfig(
        project_name=project_name,
        project_root=project_root,
        source_video=source_video
    )

    # Create project structure
    validate_project_structure(project_root, create_missing=True)

    # Save project configuration
    project_config.save()

    # Create and return orchestrator
    return PipelineOrchestrator(project_config=project_config)
