#!/usr/bin/env python3
"""
Performance monitoring and metrics collection.
"""

from __future__ import annotations

import time
import json
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime
from dataclasses import dataclass, field, asdict
from contextlib import contextmanager


@dataclass
class APICallMetric:
    """Metrics for an API call."""
    endpoint: str
    started_at: datetime
    duration_seconds: float
    success: bool
    error_message: Optional[str] = None
    tokens_used: int = 0
    cost_usd: float = 0.0


@dataclass
class FileMetric:
    """Metrics for a file operation."""
    path: str
    operation: str  # 'read', 'write', 'delete'
    size_bytes: int
    duration_seconds: float
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class StageMetric:
    """Metrics for a pipeline stage."""
    stage_name: str
    started_at: datetime
    completed_at: Optional[datetime] = None
    duration_seconds: float = 0.0
    success: bool = False
    error_message: Optional[str] = None
    files_processed: int = 0
    api_calls: int = 0
    memory_mb: float = 0.0


class StageTimer:
    """Context manager for timing pipeline stages."""

    def __init__(self, metrics_collector: MetricsCollector, stage_name: str):
        """
        Initialize stage timer.

        Args:
            metrics_collector: Metrics collector instance
            stage_name: Name of the stage being timed
        """
        self.metrics_collector = metrics_collector
        self.stage_name = stage_name
        self.start_time: Optional[float] = None
        self.metric: Optional[StageMetric] = None

    def __enter__(self) -> StageTimer:
        """Start timing the stage."""
        self.start_time = time.time()
        self.metric = StageMetric(
            stage_name=self.stage_name,
            started_at=datetime.now()
        )
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Stop timing and record the metric."""
        if self.start_time and self.metric:
            duration = time.time() - self.start_time
            self.metric.duration_seconds = duration
            self.metric.completed_at = datetime.now()

            if exc_type is None:
                self.metric.success = True
            else:
                self.metric.success = False
                self.metric.error_message = str(exc_val)

            self.metrics_collector.record_stage(self.metric)

        return False  # Don't suppress exceptions


class MetricsCollector:
    """
    Centralized metrics collection system.

    Tracks performance metrics for:
    - API calls
    - File operations
    - Pipeline stages
    - Overall execution
    """

    def __init__(self):
        """Initialize metrics collector."""
        self.started_at = datetime.now()
        self.completed_at: Optional[datetime] = None

        self.api_calls: List[APICallMetric] = []
        self.file_operations: List[FileMetric] = []
        self.stage_metrics: List[StageMetric] = []

        self._api_call_count = 0
        self._total_api_duration = 0.0
        self._total_tokens_used = 0
        self._total_cost_usd = 0.0

        self._total_files_processed = 0
        self._total_bytes_processed = 0

    def record_api_call(
        self,
        endpoint: str,
        duration: float,
        success: bool = True,
        error: Optional[str] = None,
        tokens: int = 0,
        cost: float = 0.0
    ) -> None:
        """Record an API call metric."""
        metric = APICallMetric(
            endpoint=endpoint,
            started_at=datetime.now(),
            duration_seconds=duration,
            success=success,
            error_message=error,
            tokens_used=tokens,
            cost_usd=cost
        )

        self.api_calls.append(metric)
        self._api_call_count += 1
        self._total_api_duration += duration
        self._total_tokens_used += tokens
        self._total_cost_usd += cost

    def record_file_operation(
        self,
        path: Path,
        operation: str,
        size_bytes: int,
        duration: float
    ) -> None:
        """Record a file operation metric."""
        metric = FileMetric(
            path=str(path),
            operation=operation,
            size_bytes=size_bytes,
            duration_seconds=duration
        )

        self.file_operations.append(metric)
        self._total_files_processed += 1
        self._total_bytes_processed += size_bytes

    def record_stage(self, metric: StageMetric) -> None:
        """Record a pipeline stage metric."""
        self.stage_metrics.append(metric)

    @contextmanager
    def time_stage(self, stage_name: str):
        """Context manager for timing a stage."""
        timer = StageTimer(self, stage_name)
        with timer:
            yield timer

    def complete(self) -> None:
        """Mark metrics collection as complete."""
        self.completed_at = datetime.now()

    def get_summary(self) -> Dict[str, Any]:
        """Get summary of all collected metrics."""
        total_duration = 0.0
        if self.completed_at:
            total_duration = (self.completed_at - self.started_at).total_seconds()

        successful_stages = sum(1 for m in self.stage_metrics if m.success)
        failed_stages = len(self.stage_metrics) - successful_stages

        return {
            "execution": {
                "started_at": self.started_at.isoformat(),
                "completed_at": self.completed_at.isoformat() if self.completed_at else None,
                "total_duration_seconds": total_duration,
                "stages_completed": successful_stages,
                "stages_failed": failed_stages
            },
            "api": {
                "total_calls": self._api_call_count,
                "total_duration_seconds": self._total_api_duration,
                "total_tokens_used": self._total_tokens_used,
                "total_cost_usd": self._total_cost_usd,
                "average_duration_seconds": self._total_api_duration / max(self._api_call_count, 1)
            },
            "files": {
                "total_operations": self._total_files_processed,
                "total_bytes": self._total_bytes_processed,
                "total_mb": self._total_bytes_processed / (1024 * 1024)
            },
            "stages": [
                {
                    "name": m.stage_name,
                    "duration_seconds": m.duration_seconds,
                    "success": m.success,
                    "error": m.error_message
                }
                for m in self.stage_metrics
            ]
        }

    def export_to_file(self, path: Path) -> None:
        """Export metrics to JSON file."""
        path.parent.mkdir(parents=True, exist_ok=True)

        data = {
            "summary": self.get_summary(),
            "api_calls": [asdict(call) for call in self.api_calls],
            "file_operations": [asdict(op) for op in self.file_operations],
            "stage_metrics": [
                {
                    **asdict(m),
                    "started_at": m.started_at.isoformat(),
                    "completed_at": m.completed_at.isoformat() if m.completed_at else None
                }
                for m in self.stage_metrics
            ]
        }

        # Convert datetime objects to strings
        def serialize_datetime(obj):
            if isinstance(obj, datetime):
                return obj.isoformat()
            raise TypeError(f"Object of type {type(obj)} is not JSON serializable")

        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, default=serialize_datetime)

    def print_summary(self) -> None:
        """Print a formatted summary to console."""
        summary = self.get_summary()

        print("\n" + "=" * 60)
        print("PERFORMANCE METRICS SUMMARY")
        print("=" * 60)

        # Execution summary
        print(f"\n📊 Execution:")
        print(f"   Total Duration: {summary['execution']['total_duration_seconds']:.2f}s")
        print(f"   Stages Completed: {summary['execution']['stages_completed']}")
        print(f"   Stages Failed: {summary['execution']['stages_failed']}")

        # API summary
        print(f"\n🌐 API Calls:")
        print(f"   Total Calls: {summary['api']['total_calls']}")
        print(f"   Total Duration: {summary['api']['total_duration_seconds']:.2f}s")
        print(f"   Total Tokens: {summary['api']['total_tokens_used']:,}")
        print(f"   Total Cost: ${summary['api']['total_cost_usd']:.4f}")

        # File summary
        print(f"\n📁 File Operations:")
        print(f"   Total Operations: {summary['files']['total_operations']}")
        print(f"   Total Size: {summary['files']['total_mb']:.2f} MB")

        # Stage details
        print(f"\n⚙️  Stage Performance:")
        for stage in summary['stages']:
            status = "✓" if stage['success'] else "✗"
            print(f"   {status} {stage['name']}: {stage['duration_seconds']:.2f}s")
            if stage['error']:
                print(f"      Error: {stage['error']}")

        print("\n" + "=" * 60 + "\n")


@contextmanager
def time_operation(name: str = "operation"):
    """
    Simple context manager for timing operations.

    Example:
        with time_operation("processing video") as timer:
            # Do something
            pass
        print(f"Took {timer.duration:.2f}s")
    """
    start_time = time.time()

    class Timer:
        def __init__(self):
            self.duration = 0.0

    timer = Timer()

    try:
        yield timer
    finally:
        timer.duration = time.time() - start_time
