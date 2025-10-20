#!/usr/bin/env python3
"""
Data schemas for project configuration and pipeline state management.
"""

from __future__ import annotations

from dataclasses import dataclass, field, asdict
from enum import Enum
from pathlib import Path
from typing import Optional, Dict, Any, List
from datetime import datetime
import json


class PipelineStage(Enum):
    """Pipeline execution stages."""
    INITIALIZED = "initialized"
    AUDIO_EXTRACTION = "audio_extraction"
    TRANSCRIPTION = "transcription"
    ANALYSIS = "analysis"
    SEGMENT_EXTRACTION = "segment_extraction"
    TIMESTAMP_GENERATION = "timestamp_generation"
    SUBTITLE_CREATION = "subtitle_creation"
    SUBTITLE_HARDBURN = "subtitle_hardburn"
    FINALIZATION = "finalization"
    COMPLETED = "completed"
    FAILED = "failed"


class StageStatus(Enum):
    """Status of individual stage."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class ReelConfig:
    """Configuration for a single reel segment."""
    id: str
    start: str  # Timestamp format: HH:MM:SS.mmm
    end: str    # Timestamp format: HH:MM:SS.mmm
    title: str
    subtitle: Optional[str] = None
    video_duration: Optional[str] = None
    title_position_y: Optional[int] = None
    subtitle_position_y: Optional[int] = None
    title_duration: Optional[float] = None
    word_output: Optional[str] = None
    ass_output: Optional[str] = None
    final_output: Optional[str] = None
    viral_potential: int = 0
    hook_type: str = ""

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {k: v for k, v in asdict(self).items() if v is not None}


@dataclass
class ProjectConfig:
    """Complete project configuration."""
    project_name: str
    project_root: Path
    source_video: Path
    transcript_path: Optional[Path] = None
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    version: str = "3.0.0"
    reels: List[ReelConfig] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def add_reel(self, reel: ReelConfig) -> None:
        """Add a reel configuration."""
        self.reels.append(reel)
        self.updated_at = datetime.now()

    def get_reel(self, reel_id: str) -> Optional[ReelConfig]:
        """Get reel configuration by ID."""
        for reel in self.reels:
            if reel.id == reel_id:
                return reel
        return None

    def save(self, path: Optional[Path] = None) -> None:
        """Save configuration to JSON file."""
        if path is None:
            path = self.project_root / "project_config.json"

        path.parent.mkdir(parents=True, exist_ok=True)

        data = {
            "project_name": self.project_name,
            "project_root": str(self.project_root),
            "source_video": str(self.source_video),
            "transcript_path": str(self.transcript_path) if self.transcript_path else None,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "version": self.version,
            "reels": [reel.to_dict() for reel in self.reels],
            "metadata": self.metadata
        }

        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    @classmethod
    def load(cls, path: Path) -> ProjectConfig:
        """Load configuration from JSON file."""
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        reels = [ReelConfig(**reel) for reel in data.get("reels", [])]

        return cls(
            project_name=data["project_name"],
            project_root=Path(data["project_root"]),
            source_video=Path(data["source_video"]),
            transcript_path=Path(data["transcript_path"]) if data.get("transcript_path") else None,
            created_at=datetime.fromisoformat(data.get("created_at", datetime.now().isoformat())),
            updated_at=datetime.fromisoformat(data.get("updated_at", datetime.now().isoformat())),
            version=data.get("version", "3.0.0"),
            reels=reels,
            metadata=data.get("metadata", {})
        )


@dataclass
class StageMetrics:
    """Metrics for a pipeline stage."""
    stage: str
    status: StageStatus
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    duration_seconds: float = 0.0
    error_message: Optional[str] = None
    retries: int = 0
    artifacts: Dict[str, str] = field(default_factory=dict)

    def start(self) -> None:
        """Mark stage as started."""
        self.status = StageStatus.RUNNING
        self.started_at = datetime.now()

    def complete(self) -> None:
        """Mark stage as completed."""
        self.status = StageStatus.COMPLETED
        self.completed_at = datetime.now()
        if self.started_at:
            self.duration_seconds = (self.completed_at - self.started_at).total_seconds()

    def fail(self, error: str) -> None:
        """Mark stage as failed."""
        self.status = StageStatus.FAILED
        self.completed_at = datetime.now()
        self.error_message = error
        if self.started_at:
            self.duration_seconds = (self.completed_at - self.started_at).total_seconds()

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "stage": self.stage,
            "status": self.status.value,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "duration_seconds": self.duration_seconds,
            "error_message": self.error_message,
            "retries": self.retries,
            "artifacts": self.artifacts
        }


@dataclass
class PipelineState:
    """Complete state of pipeline execution."""
    project_config: ProjectConfig
    current_stage: PipelineStage = PipelineStage.INITIALIZED
    stage_metrics: List[StageMetrics] = field(default_factory=list)
    started_at: datetime = field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None
    total_duration_seconds: float = 0.0
    success: bool = False
    error_message: Optional[str] = None
    checkpoint_path: Optional[Path] = None

    def add_stage_metric(self, stage: str) -> StageMetrics:
        """Add a new stage metric."""
        metric = StageMetrics(stage=stage, status=StageStatus.PENDING)
        self.stage_metrics.append(metric)
        return metric

    def get_stage_metric(self, stage: str) -> Optional[StageMetrics]:
        """Get metrics for a specific stage."""
        for metric in self.stage_metrics:
            if metric.stage == stage:
                return metric
        return None

    def complete(self, success: bool = True) -> None:
        """Mark pipeline as completed."""
        self.completed_at = datetime.now()
        self.total_duration_seconds = (self.completed_at - self.started_at).total_seconds()
        self.success = success
        self.current_stage = PipelineStage.COMPLETED if success else PipelineStage.FAILED

    def save_checkpoint(self, path: Optional[Path] = None) -> None:
        """Save pipeline state checkpoint."""
        if path is None:
            path = self.project_config.project_root / "Logs" / "pipeline_state.json"

        path.parent.mkdir(parents=True, exist_ok=True)
        self.checkpoint_path = path

        data = {
            "current_stage": self.current_stage.value,
            "stage_metrics": [metric.to_dict() for metric in self.stage_metrics],
            "started_at": self.started_at.isoformat(),
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "total_duration_seconds": self.total_duration_seconds,
            "success": self.success,
            "error_message": self.error_message
        }

        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)

    @classmethod
    def load_checkpoint(cls, project_config: ProjectConfig, path: Path) -> PipelineState:
        """Load pipeline state from checkpoint."""
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        state = cls(project_config=project_config)
        state.current_stage = PipelineStage(data["current_stage"])
        state.started_at = datetime.fromisoformat(data["started_at"])
        state.completed_at = datetime.fromisoformat(data["completed_at"]) if data.get("completed_at") else None
        state.total_duration_seconds = data["total_duration_seconds"]
        state.success = data["success"]
        state.error_message = data.get("error_message")
        state.checkpoint_path = path

        # Reconstruct stage metrics
        for metric_data in data["stage_metrics"]:
            metric = StageMetrics(
                stage=metric_data["stage"],
                status=StageStatus(metric_data["status"]),
                started_at=datetime.fromisoformat(metric_data["started_at"]) if metric_data.get("started_at") else None,
                completed_at=datetime.fromisoformat(metric_data["completed_at"]) if metric_data.get("completed_at") else None,
                duration_seconds=metric_data["duration_seconds"],
                error_message=metric_data.get("error_message"),
                retries=metric_data["retries"],
                artifacts=metric_data.get("artifacts", {})
            )
            state.stage_metrics.append(metric)

        return state

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for reporting."""
        return {
            "project_name": self.project_config.project_name,
            "current_stage": self.current_stage.value,
            "stage_metrics": [metric.to_dict() for metric in self.stage_metrics],
            "started_at": self.started_at.isoformat(),
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "total_duration_seconds": self.total_duration_seconds,
            "success": self.success,
            "error_message": self.error_message,
            "reels_processed": len(self.project_config.reels)
        }
