#!/usr/bin/env python3
"""
Convert timestamped words into TikTok-style ASS subtitles.
"""

from __future__ import annotations

import argparse
import re
from dataclasses import dataclass
from pathlib import Path
from typing import List, Sequence

from utils import (
    ScriptError,
    echo_error_and_exit,
    ensure_readable_file,
    ensure_writable_parent,
    milliseconds_to_ass_time,
    parse_relative_timestamp,
    load_project_config,
)

WORD_PATTERN = re.compile(r"(\S+)\s*\[\s*([^\]]+?)\s*\]")
PUNCTUATION_BREAKS = {".", "।", "?", "!", ";", ","}


@dataclass
class WordTiming:
    word: str
    start_ms: int
    end_ms: int


@dataclass
class SubtitleEvent:
    start_ms: int
    end_ms: int
    text: str


def default_ass_from_words(words_path: Path) -> Path:
    return words_path.with_name(f"{words_path.stem}_tiktok.ass")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Create TikTok-style ASS subtitles with a fixed title and one-line captions."
    )
    parser.add_argument("input", type=Path, help="Timestamped word file (output from create_reel_timestamps.py).")
    parser.add_argument("--output", type=Path, help="Destination ASS file. Defaults to config or <input>.ass.")
    parser.add_argument("--title", help="Title text (3-5 Bengali words) for the top overlay.")
    parser.add_argument("--video-duration", help="Video duration in H:MM:SS.CC format (e.g., 0:01:14.00).")
    parser.add_argument("--max-words-per-line", type=int, default=3, help="Maximum words per subtitle line (default: 3).")
    parser.add_argument("--min-line-duration", type=int, default=800, help="Minimum subtitle duration in milliseconds (default: 800).")
    parser.add_argument("--minimum-gap", type=int, default=120, help="Minimum gap (ms) between consecutive subtitles (default: 120).")
    parser.add_argument("--title-duration", type=float, help="Seconds to display the title overlay (default: 5s).")
    parser.add_argument("--title-position-y", type=int, help="Vertical pixel position for the title (default: 120).")
    parser.add_argument("--subtitle-position-y", type=int, help="Vertical pixel position for subtitles (default: 960).")
    parser.add_argument("--config", type=Path, help="Optional project configuration JSON for defaults.")
    parser.add_argument("--reel-id", help="Reel identifier within the project configuration.")
    return parser.parse_args()


def parse_video_duration(duration: str) -> int:
    try:
        hours_str, minutes_str, seconds_str = duration.split(":")
        hours = int(hours_str)
        minutes = int(minutes_str)
        seconds, centiseconds = seconds_str.split(".")
        total_seconds = hours * 3600 + minutes * 60 + int(seconds) + int(centiseconds) / 100
        return int(total_seconds * 1000)
    except ValueError as exc:
        raise ScriptError(f"Invalid video duration format: {duration}") from exc


def load_word_timings(timestamp_file: Path) -> List[WordTiming]:
    content = ensure_readable_file(timestamp_file, "timestamp file").read_text(encoding="utf-8").strip()
    matches = WORD_PATTERN.findall(content)
    if not matches:
        raise ScriptError(f"No timestamp patterns found in {timestamp_file}.")

    ordered = sorted(
        ((word, parse_relative_timestamp(relative)) for word, relative in matches),
        key=lambda item: item[1],
    )

    timings: List[WordTiming] = []
    for idx, (word, start_ms) in enumerate(ordered):
        next_start = ordered[idx + 1][1] if idx + 1 < len(ordered) else start_ms
        timings.append(WordTiming(word, start_ms, next_start))

    return timings


def build_subtitle_events(
    words: Sequence[WordTiming],
    max_words: int,
    min_duration: int,
    minimum_gap: int,
) -> List[SubtitleEvent]:
    events: List[SubtitleEvent] = []
    current_words: List[WordTiming] = []
    last_end = -minimum_gap

    def flush_buffer():
        nonlocal last_end, current_words
        if not current_words:
            return
        start = current_words[0].start_ms
        end = max(current_words[-1].end_ms, start + min_duration)
        if start <= last_end:
            start = last_end + minimum_gap
        if end <= start:
            end = start + min_duration
        text = " ".join(word.word for word in current_words)
        events.append(SubtitleEvent(start, end, text))
        last_end = end
        current_words = []

    for idx, word in enumerate(words):
        current_words.append(word)
        is_last_word = idx == len(words) - 1
        should_flush = (
            len(current_words) >= max_words
            or word.word[-1] in PUNCTUATION_BREAKS
            or is_last_word
        )
        if should_flush:
            flush_buffer()

    return events


def create_ass_header(
    title: str,
    video_duration_ms: int,
    title_y: int,
    title_duration_seconds: float,
) -> str:
    title_duration_ms = max(0, int(title_duration_seconds * 1000))
    title_end_ms = min(title_duration_ms, video_duration_ms)
    video_duration_ass = milliseconds_to_ass_time(video_duration_ms)
    title_end_ass = milliseconds_to_ass_time(title_end_ms if title_end_ms else video_duration_ms)

    return f"""[Script Info]
ScriptType: v4.00+
WrapStyle: 2
ScaledBorderAndShadow: yes
PlayResX: 608
PlayResY: 1080

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Title,Noto Sans Bengali,68,&H00FFFFFF,&H000000FF,&H00000000,&HE0000000,-1,0,0,0,100,100,0,0,1,5,0,8,15,15,920,1
Style: OneLine,Noto Sans Bengali,68,&H00FFFFFF,&H000000FF,&H00000000,&HC0000000,-1,0,0,0,100,100,0,0,1,5,0,2,15,15,130,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
Dialogue: 0,0:00:00.00,{title_end_ass},Title,,0,0,0,,{{\\pos(304,{title_y})\\an2}}{title}
"""


def write_ass_file(
    output_path: Path,
    header: str,
    events: Sequence[SubtitleEvent],
    subtitle_y: int,
) -> None:
    ensure_writable_parent(output_path)
    with output_path.open("w", encoding="utf-8") as handle:
        handle.write(header)
        for event in events:
            start = milliseconds_to_ass_time(event.start_ms)
            end = milliseconds_to_ass_time(event.end_ms)
            handle.write(
                f"Dialogue: 0,{start},{end},OneLine,,0,0,0,,{{\\pos(304,{subtitle_y})\\an2}}{event.text}\n"
            )


def main() -> None:
    args = parse_args()
    try:
        project_config = load_project_config(args.config) if args.config else None
        reel_settings = None

        if project_config:
            if not args.reel_id:
                raise ScriptError("Provide --reel-id when using --config.")
            reel_settings = project_config.get_reel(args.reel_id)
            output_candidate = args.output or reel_settings.ass_path or default_ass_from_words(reel_settings.words_path)
            title_candidate = args.title or reel_settings.title
            duration_candidate = args.video_duration or reel_settings.video_duration
            title_pos_candidate = args.title_position_y or reel_settings.title_position_y
            subtitle_pos_candidate = args.subtitle_position_y or reel_settings.subtitle_position_y
            title_duration_candidate = args.title_duration if args.title_duration is not None else reel_settings.title_duration
        else:
            output_candidate = args.output
            title_candidate = args.title
            duration_candidate = args.video_duration
            title_pos_candidate = args.title_position_y
            subtitle_pos_candidate = args.subtitle_position_y
            title_duration_candidate = args.title_duration

        if not title_candidate:
            raise ScriptError("Title text is required (use --title or provide via config).")
        if not duration_candidate:
            raise ScriptError("Video duration is required (use --video-duration or provide via config).")

        video_duration_ms = parse_video_duration(duration_candidate)
        words = load_word_timings(args.input)
        events = build_subtitle_events(
            words=words,
            max_words=max(args.max_words_per_line, 1),
            min_duration=max(args.min_line_duration, 200),
            minimum_gap=max(args.minimum_gap, 60),
        )

        if not events:
            raise ScriptError("No subtitle events were generated. Check the word timestamps input.")

        trimmed_events: List[SubtitleEvent] = []
        for event in events:
            if event.start_ms >= video_duration_ms:
                continue
            event.end_ms = min(event.end_ms, video_duration_ms)
            if event.end_ms <= event.start_ms:
                continue
            trimmed_events.append(event)

        if not trimmed_events:
            raise ScriptError("All generated subtitles fell outside the video duration.")

        output_path = output_candidate or args.input.with_suffix(".ass")
        title_position_y = title_pos_candidate if title_pos_candidate is not None else 120
        subtitle_position_y = subtitle_pos_candidate if subtitle_pos_candidate is not None else 960
        title_duration = title_duration_candidate if title_duration_candidate is not None else 5.0

        header = create_ass_header(
            title=title_candidate,
            video_duration_ms=video_duration_ms,
            title_y=title_position_y,
            title_duration_seconds=title_duration,
        )

        write_ass_file(output_path, header, trimmed_events, subtitle_position_y)

        reel_info = f" for reel '{reel_settings.reel_id}'" if reel_settings else ""
        print(f"✅ Created {output_path}{reel_info} ({len(trimmed_events)} subtitle lines).")

    except ScriptError as error:
        echo_error_and_exit(str(error))
    except Exception as error:  # pragma: no cover
        echo_error_and_exit(f"Unexpected error: {error}")


if __name__ == "__main__":
    main()
