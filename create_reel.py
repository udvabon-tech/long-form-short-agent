#!/usr/bin/env python3
"""
Complete reel creation script from timestamp range
Extracts video segment, creates subtitles, and outputs final reel
"""

import argparse
import re
import subprocess
import sys
from pathlib import Path
import textwrap


def time_to_seconds(time_str):
    """Convert timestamp [HH:MM:SS.mmm] or [MM:SS.mmm] to seconds"""
    time_str = time_str.strip('[]')
    parts = time_str.split(':')
    if len(parts) == 3:
        return int(parts[0]) * 3600 + int(parts[1]) * 60 + float(parts[2])
    elif len(parts) == 2:
        return int(parts[0]) * 60 + float(parts[1])
    return 0


def seconds_to_duration(seconds):
    """Convert seconds to H:MM:SS.CC format"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    remaining_seconds = seconds % 60
    return f"{hours}:{minutes:02d}:{remaining_seconds:06.2f}"


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


def extract_transcript_words(transcript_file, start_time, end_time):
    """Extract words from transcript for given timestamp range"""
    start_sec = time_to_seconds(start_time)
    end_sec = time_to_seconds(end_time)
    offset_seconds = start_sec
    
    words = []
    with open(transcript_file, 'r', encoding='utf-8') as f:
        for line in f:
            match = re.match(r'\[([^\]]+)\]\s*(Speaker \d+):\s*(.+)', line)
            if match:
                timestamp = match.group(1)
                text = match.group(3).strip()
                
                line_sec = time_to_seconds(f'[{timestamp}]')
                
                if start_sec <= line_sec <= end_sec:
                    adjusted_sec = line_sec - offset_seconds
                    line_words = text.split()
                    word_duration = 0.4  # 400ms per word
                    
                    for i, word in enumerate(line_words):
                        word_time = adjusted_sec + (i * word_duration)
                        words.append((word, int(word_time * 1000)))
    
    return words


def wrap_title_text(title_text, max_chars_per_line=14):
    """Split the title into multiple lines to keep it within frame bounds"""
    normalized = " ".join(title_text.split())
    if not normalized:
        return [""]
    lines = textwrap.wrap(
        normalized,
        width=max_chars_per_line,
        break_long_words=True,
        break_on_hyphens=False
    )
    return lines or [normalized]


def create_ass_subtitles(words, title_text, video_duration_str):
    """Create ASS subtitle content from words"""
    # Get first word timestamp to calculate offset
    start_offset_ms = words[0][1] if words else 0
    
    # Group words into subtitle events (later split into 3-word lines)
    subtitle_events = []
    current_words = []
    current_start_ms = None
    last_end_ms = None
    minimum_gap_ms = 100
    max_words_per_event = 9
    
    for i, (word, word_ms) in enumerate(words):
        ms = word_ms - start_offset_ms
        
        if current_start_ms is None:
            current_start_ms = ms
        
        current_words.append(word)
        
        # Create subtitle event conditions
        is_sentence_end = word.endswith(('.', '।', '?', '!'))
        is_max_length = len(current_words) >= max_words_per_event
        is_last_word = i == len(words) - 1
        
        if is_sentence_end or is_max_length or is_last_word:
            # Calculate end time
            if i < len(words) - 1:
                next_ms = words[i+1][1] - start_offset_ms
                end_ms = next_ms
            else:
                end_ms = ms + 2000
            
            # Adjust timing to avoid overlaps
            candidate_start = current_start_ms
            if last_end_ms is not None and candidate_start <= last_end_ms:
                candidate_start = last_end_ms + minimum_gap_ms
            
            if end_ms <= candidate_start:
                end_ms = candidate_start + 400
            
            # Create subtitle line
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
    
    # Create ASS content
    title_lines = wrap_title_text(title_text)
    title_ass_text = "\\N".join(title_lines)

    ass_content = f"""[Script Info]
ScriptType: v4.00+
WrapStyle: 2
ScaledBorderAndShadow: yes
PlayResX: 608
PlayResY: 1080

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Title,Noto Sans Bengali,90,&H00FFFFFF,&H000000FF,&H00000000,&HE0000000,-1,0,0,0,100,100,0,0,1,5,0,8,40,40,120,1
Style: OneLine,Noto Sans Bengali,68,&H00FFFFFF,&H000000FF,&H00000000,&HC0000000,-1,0,0,0,100,100,0,0,1,5,0,2,15,15,130,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
Dialogue: 0,0:00:00.00,{video_duration_str},Title,,0,0,0,,{{\\pos(304,40)\\an8\\q2}}{title_ass_text}
"""
    
    # Add subtitle events
    for event in subtitle_events:
        start_time = ms_to_ass_time(event['start'])
        end_time = ms_to_ass_time(event['end'])
        words = event['text'].split()
        if words:
            lines = [" ".join(words[i:i+3]) for i in range(0, len(words), 3)]
            text_with_breaks = "\\N".join(lines)
        else:
            text_with_breaks = event['text']
        ass_content += f"Dialogue: 0,{start_time},{end_time},OneLine,,0,0,0,,{text_with_breaks}\n"
    
    return ass_content, len(subtitle_events)


def run_ffmpeg_command(cmd, description):
    """Run ffmpeg command with error handling"""
    print(f"🎬 {description}...")
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"❌ Error: {result.stderr}")
            return False
        return True
    except Exception as e:
        print(f"❌ Error running command: {e}")
        return False


def create_reel(video_file, transcript_file, start_time, end_time, title, output_name=None):
    """
    Create a complete reel from video and transcript
    
    Args:
        video_file: Path to source video file
        transcript_file: Path to transcript file
        start_time: Start timestamp (e.g., "14:21.843")
        end_time: End timestamp (e.g., "16:18.063")
        title: Title text for overlay
        output_name: Optional custom output name
    """
    
    # Setup paths
    video_path = Path(video_file)
    transcript_path = Path(transcript_file)
    
    if not video_path.exists():
        print(f"❌ Video file not found: {video_file}")
        return False
    
    if not transcript_path.exists():
        print(f"❌ Transcript file not found: {transcript_file}")
        return False
    
    # Create processing directory
    processing_dir = Path("Processing")
    processing_dir.mkdir(exist_ok=True)
    
    output_dir = Path("Output")
    output_dir.mkdir(exist_ok=True)
    
    # Generate output name if not provided
    if not output_name:
        start_clean = start_time.replace(":", "").replace(".", "")
        end_clean = end_time.replace(":", "").replace(".", "")
        output_name = f"reel_{start_clean}_to_{end_clean}"
    
    # File paths
    words_file = processing_dir / f"{output_name}_words.txt"
    ass_file = processing_dir / f"{output_name}.ass"
    segment_file = processing_dir / f"{output_name}_segment.mp4"
    final_output = output_dir / f"{output_name}.mkv"
    
    print(f"📝 Creating reel: {start_time} to {end_time}")
    print(f"🎯 Title: {title}")
    
    # Step 1: Extract transcript words
    print("📖 Extracting transcript words...")
    try:
        words = extract_transcript_words(transcript_path, f"[{start_time}]", f"[{end_time}]")
        if not words:
            print("❌ No words found in the specified time range")
            return False
        
        # Save words file for debugging
        with open(words_file, 'w', encoding='utf-8') as f:
            word_strings = [f"{word} [0m{ms//1000}s{ms%1000}ms]" for word, ms in words]
            f.write(' '.join(word_strings))
        
        print(f"✅ Extracted {len(words)} words")
    except Exception as e:
        print(f"❌ Error extracting words: {e}")
        return False
    
    # Step 2: Calculate video duration
    start_sec = time_to_seconds(f"[{start_time}]")
    end_sec = time_to_seconds(f"[{end_time}]")
    duration_sec = end_sec - start_sec
    video_duration_str = seconds_to_duration(duration_sec)
    
    # Step 3: Create ASS subtitles
    print("🎨 Creating subtitles...")
    try:
        ass_content, event_count = create_ass_subtitles(words, title, video_duration_str)
        with open(ass_file, 'w', encoding='utf-8') as f:
            f.write(ass_content)
        print(f"✅ Created {event_count} subtitle events")
    except Exception as e:
        print(f"❌ Error creating subtitles: {e}")
        return False
    
    # Step 4: Extract video segment
    cmd1 = f'ffmpeg -i "{video_path}" -ss {start_time} -to {end_time} -vf "scale=608:1080:force_original_aspect_ratio=increase,crop=608:1080" -c:a copy -y "{segment_file}"'
    if not run_ffmpeg_command(cmd1, "Extracting video segment"):
        return False
    
    # Step 5: Apply subtitles
    cmd2 = f'ffmpeg -i "{segment_file}" -vf "ass={ass_file}" -c:a copy -y "{final_output}"'
    if not run_ffmpeg_command(cmd2, "Applying subtitles"):
        return False
    
    # Step 6: Verify output
    print("🔍 Verifying output...")
    verify_cmd = f'ffprobe -v error -show_entries format=duration -show_entries stream=width,height -of default=noprint_wrappers=1 "{final_output}"'
    result = subprocess.run(verify_cmd, shell=True, capture_output=True, text=True)
    
    if result.returncode == 0:
        lines = result.stdout.strip().split('\n')
        width = lines[0].split('=')[1] if '=' in lines[0] else 'unknown'
        height = lines[1].split('=')[1] if '=' in lines[1] else 'unknown'
        duration = float(lines[2].split('=')[1]) if '=' in lines[2] else 0
        
        print(f"✅ Reel created successfully!")
        print(f"📁 Output: {final_output}")
        print(f"📐 Resolution: {width}x{height}")
        print(f"⏱️  Duration: {duration:.1f} seconds")
        print(f"🎬 Subtitles: {event_count} events")
        return True
    else:
        print("❌ Failed to verify output")
        return False


def main():
    parser = argparse.ArgumentParser(description="Create TikTok reel from video timestamp range")
    parser.add_argument("video", help="Source video file path")
    parser.add_argument("transcript", help="Transcript file path")
    parser.add_argument("start", help="Start timestamp (e.g., '14:21.843')")
    parser.add_argument("end", help="End timestamp (e.g., '16:18.063')")
    parser.add_argument("title", help="Title text for overlay")
    parser.add_argument("--output", help="Custom output name (without extension)")
    
    args = parser.parse_args()
    
    success = create_reel(
        video_file=args.video,
        transcript_file=args.transcript,
        start_time=args.start,
        end_time=args.end,
        title=args.title,
        output_name=args.output
    )
    
    if not success:
        sys.exit(1)


if __name__ == "__main__":
    main()
