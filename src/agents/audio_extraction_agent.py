#!/usr/bin/env python3
"""
Agent responsible for extracting audio from source video.
"""

from __future__ import annotations

import subprocess
from pathlib import Path

from .base_agent import BaseAgent, AgentResult
from ..utils.errors import VideoProcessingError
from ..config.validators import validate_video_file


class AudioExtractionAgent(BaseAgent):
    """Extracts audio track from source video for transcription."""

    @property
    def stage_name(self) -> str:
        return "audio_extraction"

    def validate_preconditions(self) -> None:
        """Validate source video exists and is valid."""
        source_video = self.project_config.source_video

        self._check_file_exists(source_video, "source video")

        # Validate video file
        try:
            video_info = validate_video_file(source_video)
            self.logger.info(f"Source video: {video_info['width']}x{video_info['height']}, "
                           f"{video_info['duration']:.1f}s, {video_info['codec']}")

            if not video_info['has_audio']:
                raise VideoProcessingError("Source video does not have an audio track")

        except Exception as e:
            raise VideoProcessingError(f"Invalid source video: {str(e)}")

    def execute(self) -> AgentResult:
        """Extract audio from video."""
        source_video = self.project_config.source_video
        transcripts_dir = self.project_config.project_root / "Transcripts"
        self._ensure_directory(transcripts_dir)

        audio_output = transcripts_dir / "audio_30min.mp3"

        try:
            self.logger.info(f"Extracting audio to: {audio_output}")

            # Build FFmpeg command
            cmd = [
                "ffmpeg",
                "-i", str(source_video),
                "-vn",  # No video
                "-acodec", "libmp3lame",
                "-q:a", str(self.settings.transcription.audio_quality),
                "-t", str(self.settings.transcription.max_duration_seconds),
                "-y",  # Overwrite output
                str(audio_output)
            ]

            # Execute FFmpeg
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True
            )

            self.logger.info(f"✓ Audio extracted successfully")

            # Update project config
            self.project_config.metadata['audio_file'] = str(audio_output)

            return AgentResult(
                success=True,
                message="Audio extraction completed",
                artifacts={"audio_file": audio_output}
            )

        except subprocess.CalledProcessError as e:
            error_msg = f"FFmpeg failed: {e.stderr}"
            self.logger.error(error_msg)
            return AgentResult(
                success=False,
                message=error_msg,
                error=VideoProcessingError(error_msg)
            )

    def validate_postconditions(self, result: AgentResult) -> None:
        """Validate audio file was created successfully."""
        if not result.success:
            return

        audio_file = result.artifacts.get('audio_file')
        if not audio_file:
            raise VideoProcessingError("Audio file not found in result artifacts")

        self._check_file_exists(audio_file, "extracted audio")
        self._check_file_not_empty(audio_file, min_size_bytes=10000)  # At least 10 KB

        self.logger.info(f"✓ Audio file validated: {audio_file.stat().st_size:,} bytes")
