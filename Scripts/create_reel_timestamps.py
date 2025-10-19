#!/usr/bin/env python3
"""
Extract transcript segment and create word-level timestamps for reels
"""

import re
import sys

def time_to_seconds(time_str):
    """Convert [HH:MM:SS.mmm] or [MM:SS.mmm] to seconds"""
    time_str = time_str.strip('[]')
    parts = time_str.split(':')

    if len(parts) == 3:
        return int(parts[0]) * 3600 + int(parts[1]) * 60 + float(parts[2])
    elif len(parts) == 2:
        return int(parts[0]) * 60 + float(parts[1])
    return 0

def extract_transcript_segment(transcript_file, start_time, end_time):
    """Extract transcript lines for specific time segment"""

    start_sec = time_to_seconds(start_time)
    end_sec = time_to_seconds(end_time)

    lines = []
    with open(transcript_file, 'r', encoding='utf-8') as f:
        for line in f:
            match = re.match(r'\[([^\]]+)\]\s*(Speaker \d+):\s*(.+)', line)
            if match:
                timestamp = match.group(1)
                text = match.group(3).strip()

                line_sec = time_to_seconds(f"[{timestamp}]")

                if start_sec <= line_sec <= end_sec:
                    lines.append((timestamp, text))

    return lines

def create_word_timestamps(transcript_lines, start_time, output_file):
    """Create word-level timestamp file for subtitle generation"""

    offset_seconds = time_to_seconds(start_time)

    words_with_timestamps = []

    for timestamp, text in transcript_lines:
        line_sec = time_to_seconds(f"[{timestamp}]")
        adjusted_sec = line_sec - offset_seconds

        # Split text into words
        words = text.split()
        word_duration = 0.4  # 400ms per word (approximate)

        for i, word in enumerate(words):
            word_time = adjusted_sec + (i * word_duration)
            total_seconds = int(word_time)
            milliseconds = int((word_time % 1) * 1000)

            words_with_timestamps.append(f"{word} [0m{total_seconds}s{milliseconds}ms]")

    # Write to file
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(' '.join(words_with_timestamps))

    print(f"✅ Created {output_file} with {len(words_with_timestamps)} words")

# Main execution for Reel #1
if __name__ == "__main__":
    # Reel 1: [15:47.364] to [17:01.374]
    transcript_file = 'podcast_audio_30min_transcription.txt'
    start_time = '[00:15:47.364]'
    end_time = '[00:17:01.374]'
    output_file = 'reel1.txt'

    print(f"Extracting transcript segment from {start_time} to {end_time}...")
    transcript_lines = extract_transcript_segment(transcript_file, start_time, end_time)

    print(f"Found {len(transcript_lines)} transcript lines")

    print("Creating word-level timestamps...")
    create_word_timestamps(transcript_lines, start_time, output_file)
