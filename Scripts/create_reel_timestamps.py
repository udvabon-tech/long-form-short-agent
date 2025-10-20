#!/usr/bin/env python3
"""
Extract a transcript slice and create relative word-level timestamps.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path
from typing import List, Sequence, Tuple

from utils import (
    ScriptError,
    echo_error_and_exit,
    ensure_readable_file,
    ensure_writable_parent,
    load_project_config,
    iter_transcript_entries,
    parse_transcript_timestamp,
    seconds_to_relative_timestamp,
)


@dataclass
class WordTimestamp:
    word: str
    relative_seconds: float


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate word-level timestamps for a transcript segment."
    )
    parser.add_argument(
        "transcript",
        nargs="?",
        type=Path,
        help="Path to the Gemini transcript file.",
    )
    parser.add_argument(
        "--start",
        help="Start timestamp in transcript format, e.g. 00:15:47.364",
    )
    parser.add_argument(
        "--end",
        help="End timestamp in transcript format, e.g. 00:17:01.374",
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="Destination text file for the word timestamps. "
        "Defaults to the project processing directory.",
    )
    parser.add_argument(
        "--min-duration",
        type=float,
        default=0.25,
        help="Minimum seconds to allocate per transcript line when timestamps "
        "collapse (default: 0.25).",
    )
    parser.add_argument(
        "--config",
        type=Path,
        help="Optional project configuration JSON to source defaults from.",
    )
    parser.add_argument(
        "--reel-id",
        help="Reel identifier to look up inside the project configuration.",
    )
    return parser.parse_args()


def clamp_time_range(start_seconds: float, end_seconds: float) -> Tuple[float, float]:
    if end_seconds <= start_seconds:
        raise ScriptError("End timestamp must be greater than start timestamp.")
    return start_seconds, end_seconds


def slice_transcript_entries(
    entries: Sequence,
    start_seconds: float,
    end_seconds: float,
) -> List[Tuple[int, float, float, str]]:
    """
    Return a list of (index, entry_start, entry_end, text) tuples for the target window.
    """
    window: List[Tuple[int, float, float, str]] = []

    for idx, entry in enumerate(entries):
        if entry.timestamp_seconds > end_seconds:
            break
        if entry.timestamp_seconds < start_seconds:
            continue

        next_timestamp = end_seconds
        if idx + 1 < len(entries):
            next_timestamp = min(entries[idx + 1].timestamp_seconds, end_seconds)

        entry_start = max(entry.timestamp_seconds, start_seconds)
        entry_end = max(entry_start, next_timestamp)
        window.append((idx, entry_start, entry_end, entry.text))

    return window


def generate_word_timestamps(
    window: Sequence[Tuple[int, float, float, str]],
    start_seconds: float,
    min_duration: float,
) -> List[WordTimestamp]:
    words: List[WordTimestamp] = []

    for (_, entry_start, entry_end, text) in window:
        tokens = text.split()
        if not tokens:
            continue

        duration = max(entry_end - entry_start, min_duration)
        step = duration / len(tokens)

        for offset, token in enumerate(tokens):
            absolute_time = entry_start + (offset * step)
            relative_time = max(0.0, absolute_time - start_seconds)
            words.append(WordTimestamp(token, relative_time))

    return words


def write_word_file(output_path: Path, words: Sequence[WordTimestamp]) -> None:
    ensure_writable_parent(output_path)
    payload = " ".join(
        f"{word.word} [{seconds_to_relative_timestamp(word.relative_seconds)}]"
        for word in words
    )
    output_path.write_text(payload, encoding="utf-8")


def main() -> None:
    args = parse_args()
    try:
        project_config = load_project_config(args.config) if args.config else None
        reel_settings = None

        if project_config:
            if not args.reel_id:
                raise ScriptError("Provide --reel-id when using --config.")
            reel_settings = project_config.get_reel(args.reel_id)
            transcript_candidate = args.transcript or project_config.transcript_path
            output_candidate = args.output or reel_settings.words_path
            start_value = args.start or reel_settings.start
            end_value = args.end or reel_settings.end
        else:
            if not args.transcript:
                raise ScriptError("Transcript path is required when no config file is supplied.")
            transcript_candidate = args.transcript
            output_candidate = args.output
            start_value = args.start
            end_value = args.end

        if not start_value or not end_value:
            raise ScriptError("Both start and end timestamps are required (via CLI flags or config).")

        transcript_path = ensure_readable_file(transcript_candidate, "transcript")
        entries = list(iter_transcript_entries(transcript_path))
        if not entries:
            raise ScriptError("Transcript does not contain any timestamped lines.")

        start_seconds, end_seconds = clamp_time_range(
            parse_transcript_timestamp(start_value),
            parse_transcript_timestamp(end_value),
        )

        window = slice_transcript_entries(entries, start_seconds, end_seconds)
        if not window:
            raise ScriptError(
                "No transcript lines found within the requested time window."
            )

        words = generate_word_timestamps(
            window=window,
            start_seconds=start_seconds,
            min_duration=max(args.min_duration, 0.05),
        )

        if not words:
            raise ScriptError(
                "No words produced for the requested window. "
                "Ensure the transcript contains speech within the range."
            )

        output_path = output_candidate
        if not output_path:
            suffix = f"{reel_settings.reel_id}_words" if reel_settings else "segment"
            output_path = transcript_path.with_name(f"{transcript_path.stem}_{suffix}.txt")
        if reel_settings:
            print(
                f"🎯 Reel {reel_settings.reel_id}: {reel_settings.start} → {reel_settings.end}"
            )
        else:
            print(f"🎯 Segment: {start_value} → {end_value}")

        write_word_file(output_path, words)

        print(f"✅ Created {output_path} with {len(words)} words spanning "
              f"{seconds_to_relative_timestamp(words[-1].relative_seconds)}.")

    except ScriptError as error:
        echo_error_and_exit(str(error))
    except Exception as error:  # pragma: no cover
        echo_error_and_exit(f"Unexpected error: {error}")


if __name__ == "__main__":
    main()
