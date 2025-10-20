#!/usr/bin/env python3
"""
Convert timestamped words into karaoke-style ASS subtitles.
"""

from __future__ import annotations

import argparse
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List, Sequence

from utils import (
    ScriptError,
    echo_error_and_exit,
    ensure_readable_file,
    ensure_writable_parent,
    milliseconds_to_ass_time,
    parse_relative_timestamp,
)


WORD_PATTERN = re.compile(r"(\S+)\s*\[\s*([^\]]+?)\s*\]")
PUNCTUATION_BREAKS = {".", "।", "?", "!", ";", ","}


@dataclass
class WordTiming:
    word: str
    start_ms: int
    end_ms: int


@dataclass
class SubtitleBlock:
    start_ms: int
    end_ms: int
    words: Sequence[WordTiming]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Create karaoke-style ASS subtitles from timestamped words."
    )
    parser.add_argument("input", type=Path, help="Timestamped word file (output of create_reel_timestamps.py).")
    parser.add_argument("output", type=Path, help="Destination ASS file.")
    parser.add_argument("--max-words-per-line", type=int, default=3, help="Maximum words per subtitle line (default: 3).")
    parser.add_argument("--min-word-duration", type=int, default=300, help="Minimum word duration in milliseconds (default: 300).")
    parser.add_argument("--line-padding", type=int, default=120, help="Extra padding (ms) added to each line for readability (default: 120).")
    parser.add_argument("--highlight-interval", type=int, default=4, help="Highlight every Nth word in accent colour (default: 4).")
    return parser.parse_args()


def load_words(timestamp_file: Path) -> List[WordTiming]:
    content = ensure_readable_file(timestamp_file, "timestamp file").read_text(encoding="utf-8").strip()
    matches = WORD_PATTERN.findall(content)
    if not matches:
        raise ScriptError(f"No timestamp patterns found in {timestamp_file}.")

    raw_timings = []
    for word, relative in matches:
        start_ms = parse_relative_timestamp(relative)
        raw_timings.append((word, start_ms))

    raw_timings.sort(key=lambda item: item[1])

    timings: List[WordTiming] = []
    for idx, (word, start_ms) in enumerate(raw_timings):
        next_start = raw_timings[idx + 1][1] if idx + 1 < len(raw_timings) else start_ms
        timings.append(WordTiming(word, start_ms, next_start))

    return timings


def enforce_minimum_durations(words: List[WordTiming], min_duration: int) -> None:
    for idx, word in enumerate(words):
        next_start = words[idx + 1].start_ms if idx + 1 < len(words) else word.start_ms + min_duration
        target_end = max(word.start_ms + min_duration, next_start)
        if target_end <= word.start_ms:
            target_end = word.start_ms + min_duration
        word.end_ms = target_end


def build_blocks(
    words: Sequence[WordTiming],
    max_words: int,
    line_padding: int,
) -> List[SubtitleBlock]:
    blocks: List[SubtitleBlock] = []
    current: List[WordTiming] = []

    def finalize_block(buffer: List[WordTiming]) -> None:
        if not buffer:
            return
        start_ms = buffer[0].start_ms
        end_ms = max(buffer[-1].end_ms + line_padding, start_ms + line_padding)
        blocks.append(SubtitleBlock(start_ms, end_ms, list(buffer)))

    for idx, word in enumerate(words):
        current.append(word)
        is_last_word = idx == len(words) - 1
        if (
            len(current) >= max_words
            or word.word[-1] in PUNCTUATION_BREAKS
            or is_last_word
        ):
            finalize_block(current)
            current = []

    return blocks


def build_highlighted_text(
    block: SubtitleBlock,
    highlight_interval: int,
) -> str:
    parts: List[str] = []
    for i, word in enumerate(block.words):
        duration_cs = max(10, (word.end_ms - word.start_ms) // 10)
        if highlight_interval > 0 and (i % highlight_interval == 0):
            parts.append(f"{{\\k{duration_cs}\\c&H0000FF&}}{word.word}{{\\c&H00FFFFFF&}}")
        else:
            parts.append(f"{{\\k{duration_cs}}}{word.word}")
    parts.append("{\\k0}")
    return " ".join(parts)


def create_ass_header() -> str:
    return """[Script Info]
; Enhanced subtitle with word highlighting
ScriptType: v4.00+
WrapStyle: 2
ScaledBorderAndShadow: yes
PlayResX: 608
PlayResY: 1080

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: EnhancedSub,Noto Sans Bengali,75,&H00FFFFFF,&H0000FF00,&H80000000,&H00000000,0,0,0,0,100,100,0,0,3,3,0,2,40,40,240,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""


def write_ass(
    blocks: Iterable[SubtitleBlock],
    output_path: Path,
    highlight_interval: int,
) -> None:
    ensure_writable_parent(output_path)
    with output_path.open("w", encoding="utf-8") as handle:
        handle.write(create_ass_header())
        for block in blocks:
            start = milliseconds_to_ass_time(block.start_ms)
            end = milliseconds_to_ass_time(block.end_ms)
            text = build_highlighted_text(block, highlight_interval)
            handle.write(f"Dialogue: 0,{start},{end},EnhancedSub,,0,0,0,,{text}\n")


def main() -> None:
    args = parse_args()
    try:
        words = load_words(args.input)
        enforce_minimum_durations(words, max(args.min_word_duration, 50))
        blocks = build_blocks(words, max(args.max_words_per_line, 1), max(args.line_padding, 0))
        write_ass(blocks, args.output, max(args.highlight_interval, 0))
        print(f"✅ Created {args.output} with {len(blocks)} subtitle blocks.")

    except ScriptError as error:
        echo_error_and_exit(str(error))
    except Exception as error:  # pragma: no cover
        echo_error_and_exit(f"Unexpected error: {error}")


if __name__ == "__main__":
    main()
