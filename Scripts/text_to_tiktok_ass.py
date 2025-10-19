#!/usr/bin/env python3
"""
Convert timestamped text to TikTok-style ASS subtitles
- Short title at top (fixed)
- Single-line subtitle at bottom (changes with speech)
"""
import re
import sys

def parse_timestamp(ts_str):
    """Convert timestamp like '0m0s175ms' to milliseconds"""
    match = re.match(r'(\d+)m(\d+)s(\d+)ms', ts_str)
    if match:
        minutes = int(match.group(1))
        seconds = int(match.group(2))
        milliseconds = int(match.group(3))
        return (minutes * 60 + seconds) * 1000 + milliseconds
    return 0

def ms_to_ass_time(ms):
    """Convert milliseconds to ASS time format H:MM:SS.CC"""
    hours = ms // 3600000
    minutes = (ms % 3600000) // 60000
    seconds = (ms % 60000) // 1000
    centiseconds = (ms % 1000) // 10
    return f"{hours:d}:{minutes:02d}:{seconds:02d}.{centiseconds:02d}"

def create_ass_header(title_text, video_duration):
    """Create ASS header with TikTok-style formatting"""
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
Dialogue: 0,0:00:00.00,{video_duration},Title,,0,0,0,,{{\\pos(304,120)\\an2}}{title_text}
"""

def convert_to_tiktok_ass(input_file, output_file, title_text, video_duration):
    """
    Convert timestamped text to TikTok-style ASS

    Args:
        input_file: Text file with word[timestamp] format
        output_file: Output ASS file
        title_text: Short title (3-5 words) to display at top
        video_duration: Total video duration in ASS format (e.g., "0:01:14.00")
    """
    with open(input_file, 'r', encoding='utf-8') as f:
        content = f.read().strip()

    # Extract words and timestamps
    pattern = r'(\S+)\s*\[\s*([^]]+)\s*\]'
    matches = re.findall(pattern, content)

    if not matches:
        print(f"❌ No timestamp patterns found in {input_file}")
        return

    # Get the first timestamp to calculate offset
    start_offset_ms = parse_timestamp(matches[0][1]) if matches else 0

    max_words_per_line = 4

    # Group words into single-line subtitle events (3-4 words each)
    subtitle_events = []
    current_words = []
    current_start_ms = None
    last_end_ms = None
    minimum_gap_ms = 100  # Ensure subtitles do not overlap

    for i, (word, timestamp) in enumerate(matches):
        ms = parse_timestamp(timestamp) - start_offset_ms

        if current_start_ms is None:
            current_start_ms = ms

        current_words.append(word)

        # Create subtitle event every 3-4 words or at sentence boundaries
        is_sentence_end = word.endswith(('.', '।', '?', '!'))
        is_max_length = len(current_words) >= max_words_per_line
        is_last_word = i == len(matches) - 1

        if is_sentence_end or is_max_length or is_last_word:
            # Calculate end time (next word's start or +2 seconds)
            if i < len(matches) - 1:
                next_ms = parse_timestamp(matches[i+1][1]) - start_offset_ms
                end_ms = next_ms
            else:
                end_ms = ms + 2000

            candidate_start = current_start_ms
            if last_end_ms is not None and candidate_start <= last_end_ms:
                candidate_start = last_end_ms + minimum_gap_ms

            if end_ms <= candidate_start:
                end_ms = candidate_start + 400  # minimum readable duration

            # Create single-line text (join all words)
            text = " ".join(current_words)

            subtitle_events.append({
                'start': candidate_start,
                'end': end_ms,
                'text': text
            })

            # Reset for next subtitle
            current_words = []
            current_start_ms = None
            last_end_ms = end_ms

    # Write ASS file
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(create_ass_header(title_text, video_duration))

        for event in subtitle_events:
            start_time = ms_to_ass_time(event['start'])
            end_time = ms_to_ass_time(event['end'])
            line = f"Dialogue: 0,{start_time},{end_time},OneLine,,0,0,0,,{event['text']}\n"
            f.write(line)

    print(f"✅ Created {output_file}")
    print(f"   Title: {title_text}")
    print(f"   Subtitle events: {len(subtitle_events)}")

if __name__ == "__main__":
    if len(sys.argv) != 5:
        print("Usage: python text_to_tiktok_ass.py input.txt output.ass 'Title Text' 'H:MM:SS.CC'")
        print()
        print("Example:")
        print("  python text_to_tiktok_ass.py reel1.txt reel1_tiktok.ass 'আপনার মস্তিষ্ক অকেজো হচ্ছে?' '0:01:14.00'")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2]
    title_text = sys.argv[3]
    video_duration = sys.argv[4]

    convert_to_tiktok_ass(input_file, output_file, title_text, video_duration)
