#!/usr/bin/env python3
"""
Validation utilities for configuration and project structure.
"""

from __future__ import annotations

from pathlib import Path
from typing import List, Dict, Any
import subprocess
import json


class ValidationError(Exception):
    """Raised when validation fails."""
    pass


def validate_project_structure(project_root: Path, create_missing: bool = False) -> List[str]:
    """
    Validate that project has required directory structure.

    Args:
        project_root: Path to project root directory
        create_missing: If True, create missing directories

    Returns:
        List of validation messages (empty if all valid)
    """
    required_dirs = [
        "Source",
        "Transcripts",
        "Analysis",
        "Processing",
        "Output",
        "Logs"
    ]

    messages = []

    for dir_name in required_dirs:
        dir_path = project_root / dir_name
        if not dir_path.exists():
            if create_missing:
                dir_path.mkdir(parents=True, exist_ok=True)
                messages.append(f"Created missing directory: {dir_name}/")
            else:
                messages.append(f"Missing required directory: {dir_name}/")

    return messages


def validate_video_file(video_path: Path) -> Dict[str, Any]:
    """
    Validate video file and extract metadata using ffprobe.

    Args:
        video_path: Path to video file

    Returns:
        Dictionary with video metadata

    Raises:
        ValidationError: If video file is invalid
    """
    if not video_path.exists():
        raise ValidationError(f"Video file not found: {video_path}")

    if not video_path.is_file():
        raise ValidationError(f"Not a file: {video_path}")

    # Use ffprobe to extract video info
    try:
        result = subprocess.run(
            [
                "ffprobe",
                "-v", "quiet",
                "-print_format", "json",
                "-show_format",
                "-show_streams",
                str(video_path)
            ],
            capture_output=True,
            text=True,
            check=True
        )

        data = json.loads(result.stdout)

        # Extract video stream info
        video_stream = None
        audio_stream = None

        for stream in data.get("streams", []):
            if stream.get("codec_type") == "video" and not video_stream:
                video_stream = stream
            elif stream.get("codec_type") == "audio" and not audio_stream:
                audio_stream = stream

        if not video_stream:
            raise ValidationError(f"No video stream found in: {video_path}")

        format_info = data.get("format", {})

        return {
            "width": int(video_stream.get("width", 0)),
            "height": int(video_stream.get("height", 0)),
            "duration": float(format_info.get("duration", 0)),
            "size_bytes": int(format_info.get("size", 0)),
            "codec": video_stream.get("codec_name", "unknown"),
            "has_audio": audio_stream is not None,
            "audio_codec": audio_stream.get("codec_name", "none") if audio_stream else "none",
            "format": format_info.get("format_name", "unknown")
        }

    except subprocess.CalledProcessError as e:
        raise ValidationError(f"Failed to probe video file: {e.stderr}")
    except json.JSONDecodeError:
        raise ValidationError("Failed to parse ffprobe output")
    except Exception as e:
        raise ValidationError(f"Error validating video: {str(e)}")


def validate_audio_file(audio_path: Path) -> Dict[str, Any]:
    """
    Validate audio file and extract metadata.

    Args:
        audio_path: Path to audio file

    Returns:
        Dictionary with audio metadata

    Raises:
        ValidationError: If audio file is invalid
    """
    if not audio_path.exists():
        raise ValidationError(f"Audio file not found: {audio_path}")

    try:
        result = subprocess.run(
            [
                "ffprobe",
                "-v", "quiet",
                "-print_format", "json",
                "-show_format",
                "-show_streams",
                str(audio_path)
            ],
            capture_output=True,
            text=True,
            check=True
        )

        data = json.loads(result.stdout)

        audio_stream = None
        for stream in data.get("streams", []):
            if stream.get("codec_type") == "audio":
                audio_stream = stream
                break

        if not audio_stream:
            raise ValidationError(f"No audio stream found in: {audio_path}")

        format_info = data.get("format", {})

        return {
            "duration": float(format_info.get("duration", 0)),
            "size_bytes": int(format_info.get("size", 0)),
            "codec": audio_stream.get("codec_name", "unknown"),
            "sample_rate": int(audio_stream.get("sample_rate", 0)),
            "channels": int(audio_stream.get("channels", 0))
        }

    except subprocess.CalledProcessError as e:
        raise ValidationError(f"Failed to probe audio file: {e.stderr}")
    except json.JSONDecodeError:
        raise ValidationError("Failed to parse ffprobe output")
    except Exception as e:
        raise ValidationError(f"Error validating audio: {str(e)}")


def validate_transcript_file(transcript_path: Path) -> Dict[str, Any]:
    """
    Validate transcript file format and content.

    Args:
        transcript_path: Path to transcript file

    Returns:
        Dictionary with transcript statistics

    Raises:
        ValidationError: If transcript is invalid
    """
    if not transcript_path.exists():
        raise ValidationError(f"Transcript file not found: {transcript_path}")

    try:
        content = transcript_path.read_text(encoding='utf-8')
    except UnicodeDecodeError:
        raise ValidationError(f"Transcript is not valid UTF-8: {transcript_path}")

    if not content.strip():
        raise ValidationError(f"Transcript file is empty: {transcript_path}")

    # Count timestamp entries
    import re
    timestamp_pattern = re.compile(r'\[[\d:.]+\]')
    timestamps = timestamp_pattern.findall(content)

    lines = content.splitlines()
    non_empty_lines = [line for line in lines if line.strip()]

    return {
        "total_lines": len(lines),
        "non_empty_lines": len(non_empty_lines),
        "timestamps": len(timestamps),
        "size_bytes": len(content.encode('utf-8')),
        "has_timestamps": len(timestamps) > 0
    }


def validate_ffmpeg_installation() -> Dict[str, Any]:
    """
    Validate FFmpeg installation and capabilities.

    Returns:
        Dictionary with FFmpeg info

    Raises:
        ValidationError: If FFmpeg is not properly installed
    """
    try:
        result = subprocess.run(
            ["ffmpeg", "-version"],
            capture_output=True,
            text=True,
            check=True
        )

        version_line = result.stdout.splitlines()[0] if result.stdout else ""
        has_libass = "--enable-libass" in result.stdout

        if not has_libass:
            raise ValidationError(
                "FFmpeg is installed but does not have libass support.\n"
                "libass is required for Bengali subtitle rendering.\n"
                "Please reinstall FFmpeg with --enable-libass"
            )

        return {
            "installed": True,
            "version": version_line,
            "has_libass": has_libass
        }

    except FileNotFoundError:
        raise ValidationError(
            "FFmpeg is not installed or not in PATH.\n"
            "Install with: brew install ffmpeg (macOS) or sudo apt install ffmpeg (Linux)"
        )
    except subprocess.CalledProcessError as e:
        raise ValidationError(f"Error running ffmpeg: {e.stderr}")


def validate_config(config: Dict[str, Any]) -> List[str]:
    """
    Validate configuration dictionary.

    Args:
        config: Configuration dictionary to validate

    Returns:
        List of validation errors (empty if valid)
    """
    errors = []

    # Required top-level keys
    required_keys = ["project_name", "project_root", "source_video"]
    for key in required_keys:
        if key not in config:
            errors.append(f"Missing required config key: {key}")

    # Validate project root exists
    if "project_root" in config:
        project_root = Path(config["project_root"])
        if not project_root.exists():
            errors.append(f"Project root does not exist: {project_root}")

    # Validate source video exists
    if "source_video" in config:
        source_video = Path(config["source_video"])
        if not source_video.exists():
            errors.append(f"Source video does not exist: {source_video}")

    # Validate reels if present
    if "reels" in config:
        reels = config["reels"]
        if not isinstance(reels, list):
            errors.append("'reels' must be a list")
        else:
            for idx, reel in enumerate(reels):
                if not isinstance(reel, dict):
                    errors.append(f"Reel {idx} is not a dictionary")
                    continue

                # Check required reel fields
                required_reel_fields = ["id", "start", "end", "title"]
                for field in required_reel_fields:
                    if field not in reel:
                        errors.append(f"Reel {idx} missing required field: {field}")

    return errors


def validate_dependencies() -> Dict[str, bool]:
    """
    Validate all system dependencies.

    Returns:
        Dictionary mapping dependency name to availability
    """
    dependencies = {}

    # Check FFmpeg
    try:
        validate_ffmpeg_installation()
        dependencies["ffmpeg"] = True
    except ValidationError:
        dependencies["ffmpeg"] = False

    # Check Python packages
    try:
        import google.generativeai
        dependencies["google-generativeai"] = True
    except ImportError:
        dependencies["google-generativeai"] = False

    try:
        import yaml
        dependencies["pyyaml"] = True
    except ImportError:
        dependencies["pyyaml"] = False

    return dependencies
