#!/usr/bin/env python3
"""
Shared utility helpers for the Long Form to Shorts automation scripts.
"""

from __future__ import annotations

import os
import sys
import json
from dataclasses import dataclass
from pathlib import Path
import re
from typing import Iterable, Iterator, Optional, Tuple

_TRANSCRIPT_TIMESTAMP_RE = re.compile(r"\[?(?P<ts>[0-9:.]+)\]?")
_RELATIVE_TIMESTAMP_RE = re.compile(
    r"^\s*(?:(?P<minutes>\d+)m)?(?:(?P<seconds>\d+)s)?(?:(?P<milliseconds>\d+)ms)?\s*$",
    re.IGNORECASE,
)


class ScriptError(RuntimeError):
    """Base exception for script errors that should surface to the CLI."""


def load_required_env_var(var_name: str) -> str:
    """
    Fetch an environment variable or raise a friendly error if missing.
    """
    value = os.environ.get(var_name)
    if value:
        return value

    raise ScriptError(
        f"Environment variable {var_name} is not set.\n"
        f"Export it in your shell first, for example:\n"
        f'    export {var_name}="your-api-key-here"'
    )


def ensure_readable_file(path: Path, description: str = "file") -> Path:
    """
    Ensure the provided path exists and is a readable file.
    """
    path = path.expanduser().resolve()
    if not path.exists():
        raise ScriptError(f"{description.capitalize()} not found: {path}")
    if not path.is_file():
        raise ScriptError(f"{description.capitalize()} is not a file: {path}")
    return path


def ensure_writable_parent(path: Path) -> Path:
    """
    Ensure the parent directory of the target path exists.
    """
    path = path.expanduser().resolve()
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


def parse_transcript_timestamp(raw_timestamp: str) -> float:
    """
    Convert transcript timestamps like [HH:MM:SS.mmm] or [MM:SS.mmm] into seconds.
    """
    match = _TRANSCRIPT_TIMESTAMP_RE.match(raw_timestamp.strip())
    if not match:
        raise ScriptError(f"Unrecognised timestamp format: {raw_timestamp}")

    ts = match.group("ts")
    parts = ts.split(":")
    try:
        if len(parts) == 3:
            hours, minutes, seconds = parts
            return (
                int(hours) * 3600
                + int(minutes) * 60
                + float(seconds)
            )
        if len(parts) == 2:
            minutes, seconds = parts
            return int(minutes) * 60 + float(seconds)
    except ValueError as exc:
        raise ScriptError(f"Invalid timestamp component in: {raw_timestamp}") from exc

    raise ScriptError(f"Unsupported timestamp format: {raw_timestamp}")


def seconds_to_transcript_timestamp(seconds: float) -> str:
    """
    Convert seconds back into the canonical [HH:MM:SS.mmm] transcript format.
    """
    if seconds < 0:
        seconds = 0.0

    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    sec = seconds % 60
    return f"[{hours:02d}:{minutes:02d}:{sec:06.3f}]"


def parse_relative_timestamp(relative: str) -> int:
    """
    Parse relative timestamps produced by the timestamp scripts (XmYsZms) into milliseconds.
    """
    match = _RELATIVE_TIMESTAMP_RE.match(relative)
    if not match:
        raise ScriptError(f"Unrecognised relative timestamp: {relative}")

    minutes = int(match.group("minutes") or 0)
    seconds = int(match.group("seconds") or 0)
    milliseconds = int(match.group("milliseconds") or 0)
    return (minutes * 60 + seconds) * 1000 + milliseconds


def milliseconds_to_ass_time(ms: int) -> str:
    """
    Convert milliseconds to ASS timestamp format H:MM:SS.CC.
    """
    if ms < 0:
        ms = 0

    hours = ms // 3_600_000
    minutes = (ms % 3_600_000) // 60_000
    seconds = (ms % 60_000) // 1_000
    centiseconds = (ms % 1_000) // 10
    return f"{hours}:{minutes:02d}:{seconds:02d}.{centiseconds:02d}"


def seconds_to_relative_timestamp(seconds: float) -> str:
    """
    Represent seconds as XmYsZms relative timestamp strings used by subtitle scripts.
    """
    total_ms = max(0, int(round(seconds * 1000)))
    minutes = total_ms // 60_000
    seconds_component = (total_ms % 60_000) // 1_000
    milliseconds = total_ms % 1_000
    return f"{minutes}m{seconds_component}s{milliseconds:03d}ms"


def echo_error_and_exit(message: str) -> None:
    """
    Print an error message and exit the script with status code 1.
    """
    print(f"❌ {message}", file=sys.stderr)
    sys.exit(1)


@dataclass
class TranscriptEntry:
    timestamp_seconds: float
    speaker: Optional[str]
    text: str


_TRANSCRIPT_LINE_RE = re.compile(
    r"^\s*\[(?P<timestamp>[^\]]+)\]\s*(?:(?P<speaker>Speaker\s+\d+):)?\s*(?P<text>.*\S)\s*$"
)


def iter_transcript_entries(transcript_path: Path) -> Iterator[TranscriptEntry]:
    """
    Yield parsed entries from a Gemini transcript file.
    """
    with transcript_path.open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            match = _TRANSCRIPT_LINE_RE.match(line)
            if not match:
                # Skip blank lines but warn about malformed content
                if line.strip():
                    raise ScriptError(
                        f"Malformed transcript line {line_number} in {transcript_path}"
                    )
                continue

            timestamp = parse_transcript_timestamp(match.group("timestamp"))
            speaker = match.group("speaker")
            text = match.group("text").strip()
            if not text:
                continue
            yield TranscriptEntry(timestamp, speaker, text)


def chunk_iterable(iterable: Iterable, size: int) -> Iterator[Tuple]:
    """
    Yield successive fixed-size chunks from an iterable.
    """
    chunk = []
    for item in iterable:
        chunk.append(item)
        if len(chunk) == size:
            yield tuple(chunk)
            chunk = []
    if chunk:
        yield tuple(chunk)


@dataclass
class ReelSettings:
    reel_id: str
    start: str
    end: str
    words_path: Path
    ass_path: Optional[Path]
    title: Optional[str] = None
    subtitle: Optional[str] = None
    video_duration: Optional[str] = None
    title_position_y: Optional[int] = None
    subtitle_position_y: Optional[int] = None
    title_duration: Optional[float] = None
    final_output: Optional[Path] = None


@dataclass
class ProjectConfig:
    path: Path
    project_root: Path
    transcript_path: Path
    reels: dict[str, ReelSettings]

    def get_reel(self, reel_id: str) -> ReelSettings:
        try:
            return self.reels[reel_id]
        except KeyError as exc:
            raise ScriptError(f"Reel '{reel_id}' not found in configuration {self.path}") from exc


def _resolve_path(base: Path, candidate: str) -> Path:
    candidate_path = Path(candidate).expanduser()
    if candidate_path.is_absolute():
        return candidate_path.resolve()
    return (base / candidate_path).resolve()


def load_project_config(config_path: Path) -> ProjectConfig:
    config_path = ensure_readable_file(config_path, "config file")
    base_dir = config_path.parent

    try:
        data = json.loads(config_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ScriptError(f"Failed to parse JSON config {config_path}: {exc}") from exc

    project_root = _resolve_path(base_dir, data.get("project_root", "."))

    transcript_value = data.get("transcript")
    if not transcript_value:
        raise ScriptError(f"'transcript' key missing in config {config_path}")
    transcript_path = _resolve_path(project_root, transcript_value)

    reels_data = data.get("reels") or []
    if not reels_data:
        raise ScriptError(f"No reels defined in config {config_path}")

    reels: dict[str, ReelSettings] = {}
    for reel in reels_data:
        reel_id = reel.get("id")
        if not reel_id:
            raise ScriptError(f"Found reel entry without an 'id' in {config_path}")

        start = reel.get("start")
        end = reel.get("end")
        if not start or not end:
            raise ScriptError(f"Reel '{reel_id}' is missing start/end timestamps in {config_path}")

        words_output = reel.get("word_output") or f"Processing/{reel_id}.txt"
        ass_output = reel.get("ass_output")

        reels[reel_id] = ReelSettings(
            reel_id=reel_id,
            start=start,
            end=end,
            words_path=_resolve_path(project_root, words_output),
            ass_path=_resolve_path(project_root, ass_output) if ass_output else None,
            title=reel.get("title"),
            subtitle=reel.get("subtitle"),
            video_duration=reel.get("video_duration"),
            title_position_y=reel.get("title_position_y"),
            subtitle_position_y=reel.get("subtitle_position_y"),
            title_duration=reel.get("title_duration"),
            final_output=_resolve_path(project_root, reel.get("final_output")) if reel.get("final_output") else None,
        )

    return ProjectConfig(
        path=config_path,
        project_root=project_root,
        transcript_path=transcript_path,
        reels=reels,
    )
