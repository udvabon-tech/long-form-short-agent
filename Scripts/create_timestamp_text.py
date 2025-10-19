#!/usr/bin/env python3
"""
Convert transcript segment to word-level timestamp format for ASS subtitle generation
"""

import re
import sys

def convert_time_to_format(timestamp_str):
    """Convert [HH:MM:SS.mmm] or [MM:SS.mmm] to [0mXs123ms] format"""
    timestamp_str = timestamp_str.strip('[]')
    parts = timestamp_str.split(':')

    if len(parts) == 3:
        # HH:MM:SS.mmm format
        hours = int(parts[0])
        minutes = int(parts[1])
        seconds_parts = parts[2].split('.')
        seconds = int(seconds_parts[0])
        milliseconds = int(seconds_parts[1])

        total_minutes = hours * 60 + minutes
        total_seconds = total_minutes * 60 + seconds
    elif len(parts) == 2:
        # MM:SS.mmm format
        minutes = int(parts[0])
        seconds_parts = parts[1].split('.')
        seconds = int(seconds_parts[0])
        milliseconds = int(seconds_parts[1])

        total_seconds = minutes * 60 + seconds
    else:
        return None

    # Convert to [0mXs123ms] format
    return f"[0m{total_seconds}s{milliseconds}ms]"

def process_transcript(input_file, start_time, end_time, output_file, offset_seconds=0):
    """
    Process transcript and create word-level timestamp file

    Args:
        input_file: Path to transcript file
        start_time: Start time in [HH:MM:SS.mmm] or [MM:SS.mmm] format
        end_time: End time in same format
        output_file: Output text file path
        offset_seconds: Time offset to subtract (to start from 0)
    """

    def time_to_seconds(time_str):
        """Convert timestamp to seconds"""
        time_str = time_str.strip('[]')
        parts = time_str.split(':')
        if len(parts) == 3:
            return int(parts[0]) * 3600 + int(parts[1]) * 60 + float(parts[2])
        elif len(parts) == 2:
            return int(parts[0]) * 60 + float(parts[1])
        return 0

    start_sec = time_to_seconds(start_time)
    end_sec = time_to_seconds(end_time)

    # Calculate offset from first timestamp
    if offset_seconds == 0:
        offset_seconds = start_sec

    lines = []
    with open(input_file, 'r', encoding='utf-8') as f:
        for line in f:
            match = re.match(r'\[([^\]]+)\]\s*(Speaker \d+):\s*(.+)', line)
            if match:
                timestamp = match.group(1)
                text = match.group(3).strip()

                line_sec = time_to_seconds(f"[{timestamp}]")

                if start_sec <= line_sec <= end_sec:
                    # Adjust timestamp by offset
                    adjusted_sec = line_sec - offset_seconds

                    # Split text into words and assign approximate timestamps
                    words = text.split()
                    word_duration = 0.4  # Approximate 400ms per word

                    for i, word in enumerate(words):
                        word_time = adjusted_sec + (i * word_duration)
                        mins = int(word_time // 60)
                        secs = int(word_time % 60)
                        ms = int((word_time % 1) * 1000)

                        lines.append(f"{word} [0m{int(word_time)}s{ms}ms]")

    # Write output file
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(' '.join(lines))

    print(f"✅ Created {output_file}")
    print(f"   Total words: {len(lines)}")
    print(f"   Time range: {start_time} to {end_time}")
    print(f"   Offset applied: {offset_seconds:.3f}s")

if __name__ == '__main__':
    # REEL #2 configuration
    process_transcript(
        input_file='আপনি কি জানেন ২০২৫ সালে AI আপনাকে কোটিপতি বানাতে পারে - Part 1_transcription.txt',
        start_time='[03:27.177]',
        end_time='[04:21.017]',
        output_file='Reels Output/reel2.txt'
    )
