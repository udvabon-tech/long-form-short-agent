#!/usr/bin/env python3
"""
Centralized configuration management for the Long Form to Shorts system.
"""

from __future__ import annotations

import os
import yaml
from pathlib import Path
from typing import Any, Dict, Optional
from dataclasses import dataclass, field


@dataclass
class SystemSettings:
    """System-level configuration."""
    version: str = "3.0.0"
    project_root: Path = Path(".")
    log_level: str = "INFO"
    log_dir: Path = Path("logs")
    max_workers: int = 4


@dataclass
class APISettings:
    """API configuration for external services."""
    gemini_model: str = "gemini-2.5-pro"
    gemini_api_key: Optional[str] = None
    max_retries: int = 3
    timeout_seconds: int = 300
    rate_limit_delay: float = 1.0


@dataclass
class VideoSettings:
    """Video processing configuration."""
    output_format: str = "mkv"
    codec: str = "h264"
    audio_codec: str = "aac"
    default_format: str = "tiktok"

    # Format specifications
    tiktok_width: int = 608
    tiktok_height: int = 1080
    instagram_width: int = 1080
    instagram_height: int = 1920

    # Quality
    crf: int = 23
    preset: str = "medium"
    audio_bitrate: str = "128k"

    def get_dimensions(self, format_name: str = "tiktok") -> tuple[int, int]:
        """Get width and height for specified format."""
        if format_name == "instagram":
            return (self.instagram_width, self.instagram_height)
        return (self.tiktok_width, self.tiktok_height)


@dataclass
class SubtitleSettings:
    """Subtitle generation configuration."""
    font_family: str = "Noto Sans Bengali"
    title_font_size: int = 68
    subtitle_font_size: int = 68
    title_position_y: int = 120
    subtitle_position_y: int = 960
    title_duration_seconds: float = 5.0
    max_words_per_line: int = 3
    min_line_duration_ms: int = 800
    minimum_gap_ms: int = 120
    text_color: str = "#FFFFFF"
    outline_color: str = "#000000"
    background_opacity: float = 0.8
    bold: bool = True


@dataclass
class TranscriptionSettings:
    """Transcription configuration."""
    audio_format: str = "mp3"
    audio_quality: int = 2
    max_duration_seconds: int = 1800
    timestamp_format: str = "[HH:MM:SS.mmm]"
    min_segment_duration_seconds: float = 0.25


@dataclass
class AnalysisSettings:
    """Content analysis configuration."""
    max_reels: int = 3
    min_duration_seconds: int = 30
    max_duration_seconds: int = 90
    hook_types: list[str] = field(default_factory=lambda: [
        "Mind-Blowing Stat",
        "Fear/Shock",
        "Problem-Solution",
        "Contrarian",
        "Emotional"
    ])
    min_viral_potential: int = 3


@dataclass
class PipelineSettings:
    """Pipeline execution configuration."""
    stages: list[str] = field(default_factory=lambda: [
        "audio_extraction",
        "transcription",
        "analysis",
        "segment_extraction",
        "timestamp_generation",
        "subtitle_creation",
        "subtitle_hardburn",
        "finalization"
    ])
    check_file_exists: bool = True
    check_file_size: bool = True
    check_duration: bool = True
    check_dimensions: bool = True
    keep_intermediate_files: bool = True
    archive_after_days: int = 30


@dataclass
class ErrorHandlingSettings:
    """Error handling configuration."""
    max_retries: int = 3
    retry_delay_seconds: float = 2.0
    exponential_backoff: bool = True
    continue_on_error: bool = False
    save_checkpoints: bool = True


@dataclass
class MonitoringSettings:
    """Performance monitoring configuration."""
    enabled: bool = True
    track_stage_timing: bool = True
    track_file_sizes: bool = True
    track_api_calls: bool = True
    export_metrics: bool = True
    metrics_file: str = "metrics.json"


class Settings:
    """
    Centralized settings manager for the entire system.
    Loads configuration from YAML file and environment variables.
    """

    def __init__(self, config_path: Optional[Path] = None):
        """Initialize settings from config file."""
        self.config_path = config_path or Path("config.yaml")
        self._raw_config: Dict[str, Any] = {}

        # Load configuration
        self._load_config()

        # Initialize settings sections
        self.system = self._load_system_settings()
        self.api = self._load_api_settings()
        self.video = self._load_video_settings()
        self.subtitle = self._load_subtitle_settings()
        self.transcription = self._load_transcription_settings()
        self.analysis = self._load_analysis_settings()
        self.pipeline = self._load_pipeline_settings()
        self.error_handling = self._load_error_handling_settings()
        self.monitoring = self._load_monitoring_settings()

    def _load_config(self) -> None:
        """Load configuration from YAML file."""
        if not self.config_path.exists():
            raise FileNotFoundError(
                f"Configuration file not found: {self.config_path}\n"
                "Please ensure config.yaml exists in the project root."
            )

        with open(self.config_path, 'r', encoding='utf-8') as f:
            self._raw_config = yaml.safe_load(f) or {}

    def _get_section(self, section: str) -> Dict[str, Any]:
        """Get configuration section."""
        return self._raw_config.get(section, {})

    def _load_system_settings(self) -> SystemSettings:
        """Load system configuration."""
        config = self._get_section("system")
        return SystemSettings(
            version=config.get("version", "3.0.0"),
            project_root=Path(config.get("project_root", ".")),
            log_level=config.get("log_level", "INFO"),
            log_dir=Path(config.get("log_dir", "logs")),
            max_workers=config.get("max_workers", 4)
        )

    def _load_api_settings(self) -> APISettings:
        """Load API configuration."""
        config = self._get_section("api").get("gemini", {})

        # Load API key from environment
        api_key = os.environ.get("GEMINI_API_KEY")

        return APISettings(
            gemini_model=config.get("model", "gemini-2.5-pro"),
            gemini_api_key=api_key,
            max_retries=config.get("max_retries", 3),
            timeout_seconds=config.get("timeout_seconds", 300),
            rate_limit_delay=config.get("rate_limit_delay", 1.0)
        )

    def _load_video_settings(self) -> VideoSettings:
        """Load video processing configuration."""
        config = self._get_section("video")
        formats = config.get("formats", {})
        quality = config.get("quality", {})

        return VideoSettings(
            output_format=config.get("output_format", "mkv"),
            codec=config.get("codec", "h264"),
            audio_codec=config.get("audio_codec", "aac"),
            default_format=config.get("default_format", "tiktok"),
            tiktok_width=formats.get("tiktok", {}).get("width", 608),
            tiktok_height=formats.get("tiktok", {}).get("height", 1080),
            instagram_width=formats.get("instagram", {}).get("width", 1080),
            instagram_height=formats.get("instagram", {}).get("height", 1920),
            crf=quality.get("crf", 23),
            preset=quality.get("preset", "medium"),
            audio_bitrate=quality.get("audio_bitrate", "128k")
        )

    def _load_subtitle_settings(self) -> SubtitleSettings:
        """Load subtitle configuration."""
        config = self._get_section("subtitle")
        return SubtitleSettings(
            font_family=config.get("font_family", "Noto Sans Bengali"),
            title_font_size=config.get("title_font_size", 68),
            subtitle_font_size=config.get("subtitle_font_size", 68),
            title_position_y=config.get("title_position_y", 120),
            subtitle_position_y=config.get("subtitle_position_y", 960),
            title_duration_seconds=config.get("title_duration_seconds", 5.0),
            max_words_per_line=config.get("max_words_per_line", 4),
            min_line_duration_ms=config.get("min_line_duration_ms", 800),
            minimum_gap_ms=config.get("minimum_gap_ms", 120),
            text_color=config.get("text_color", "#FFFFFF"),
            outline_color=config.get("outline_color", "#000000"),
            background_opacity=config.get("background_opacity", 0.8),
            bold=config.get("bold", True)
        )

    def _load_transcription_settings(self) -> TranscriptionSettings:
        """Load transcription configuration."""
        config = self._get_section("transcription")
        return TranscriptionSettings(
            audio_format=config.get("audio_format", "mp3"),
            audio_quality=config.get("audio_quality", 2),
            max_duration_seconds=config.get("max_duration_seconds", 1800),
            timestamp_format=config.get("timestamp_format", "[HH:MM:SS.mmm]"),
            min_segment_duration_seconds=config.get("min_segment_duration_seconds", 0.25)
        )

    def _load_analysis_settings(self) -> AnalysisSettings:
        """Load analysis configuration."""
        config = self._get_section("analysis")
        ideal = config.get("ideal_duration", {})

        return AnalysisSettings(
            max_reels=config.get("max_reels", 3),
            min_duration_seconds=ideal.get("min_seconds", 30),
            max_duration_seconds=ideal.get("max_seconds", 90),
            hook_types=config.get("hook_types", [
                "Mind-Blowing Stat",
                "Fear/Shock",
                "Problem-Solution",
                "Contrarian",
                "Emotional"
            ]),
            min_viral_potential=config.get("min_viral_potential", 3)
        )

    def _load_pipeline_settings(self) -> PipelineSettings:
        """Load pipeline configuration."""
        config = self._get_section("pipeline")
        validation = config.get("validation", {})
        cleanup = config.get("cleanup", {})

        return PipelineSettings(
            stages=config.get("stages", [
                "audio_extraction",
                "transcription",
                "analysis",
                "segment_extraction",
                "timestamp_generation",
                "subtitle_creation",
                "subtitle_hardburn",
                "finalization"
            ]),
            check_file_exists=validation.get("check_file_exists", True),
            check_file_size=validation.get("check_file_size", True),
            check_duration=validation.get("check_duration", True),
            check_dimensions=validation.get("check_dimensions", True),
            keep_intermediate_files=cleanup.get("keep_intermediate_files", True),
            archive_after_days=cleanup.get("archive_after_days", 30)
        )

    def _load_error_handling_settings(self) -> ErrorHandlingSettings:
        """Load error handling configuration."""
        config = self._get_section("error_handling")
        return ErrorHandlingSettings(
            max_retries=config.get("max_retries", 3),
            retry_delay_seconds=config.get("retry_delay_seconds", 2.0),
            exponential_backoff=config.get("exponential_backoff", True),
            continue_on_error=config.get("continue_on_error", False),
            save_checkpoints=config.get("save_checkpoints", True)
        )

    def _load_monitoring_settings(self) -> MonitoringSettings:
        """Load monitoring configuration."""
        config = self._get_section("monitoring")
        return MonitoringSettings(
            enabled=config.get("enabled", True),
            track_stage_timing=config.get("track_stage_timing", True),
            track_file_sizes=config.get("track_file_sizes", True),
            track_api_calls=config.get("track_api_calls", True),
            export_metrics=config.get("export_metrics", True),
            metrics_file=config.get("metrics_file", "metrics.json")
        )

    def validate(self) -> list[str]:
        """
        Validate all settings and return list of errors.
        Returns empty list if all settings are valid.
        """
        errors = []

        # Validate API key
        if not self.api.gemini_api_key:
            errors.append("GEMINI_API_KEY environment variable is not set")

        # Validate paths
        if not self.system.project_root.exists():
            errors.append(f"Project root does not exist: {self.system.project_root}")

        # Validate numeric ranges
        if self.video.crf < 0 or self.video.crf > 51:
            errors.append(f"Invalid CRF value: {self.video.crf} (must be 0-51)")

        if self.analysis.max_reels < 1:
            errors.append(f"Invalid max_reels: {self.analysis.max_reels} (must be >= 1)")

        if self.analysis.min_duration_seconds >= self.analysis.max_duration_seconds:
            errors.append("min_duration_seconds must be less than max_duration_seconds")

        return errors


def load_settings(config_path: Optional[Path] = None) -> Settings:
    """
    Load and validate settings from configuration file.

    Args:
        config_path: Optional path to config file (defaults to config.yaml)

    Returns:
        Settings instance

    Raises:
        ValueError: If configuration is invalid
    """
    settings = Settings(config_path)

    # Validate settings
    errors = settings.validate()
    if errors:
        raise ValueError(
            "Configuration validation failed:\n" +
            "\n".join(f"  - {error}" for error in errors)
        )

    return settings
