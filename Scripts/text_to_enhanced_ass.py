#!/usr/bin/env python3
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

def create_ass_header():
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

def build_highlighted_text(words_with_timing):
    """Build ASS text with word-level highlighting"""
    parts = []
    
    for i, (word, start_ms, end_ms) in enumerate(words_with_timing):
        # Calculate duration for this word in centiseconds
        duration_cs = max(10, (end_ms - start_ms) // 10)
        
        # Alternate between green and red highlighting (every 4th word gets red)
        if i % 4 == 0:
            # Red highlight for emphasis
            parts.append(f"{{\\k{duration_cs}\\c&H0000FF&}}{word}{{\\c&H00FFFFFF&}}")
        else:
            # Green highlight (default secondary color)
            parts.append(f"{{\\k{duration_cs}}}{word}")
    
    # Add final reset
    parts.append("{\\k0}")
    return " ".join(parts)

def convert_text_to_enhanced_ass(input_file, output_file):
    with open(input_file, 'r', encoding='utf-8') as f:
        content = f.read().strip()
    
    # Extract words and timestamps
    pattern = r'(\S+)\s*\[\s*([^]]+)\s*\]'
    matches = re.findall(pattern, content)
    
    if not matches:
        print("No timestamp patterns found")
        return
    
    # Group words into subtitle blocks (2-3 words each)
    subtitle_blocks = []
    current_block = []
    current_word_timings = []
    
    # Get the first timestamp to calculate offset
    start_offset_ms = parse_timestamp(matches[0][1]) if matches else 0
    
    for i, (word, timestamp) in enumerate(matches):
        ms = parse_timestamp(timestamp) - start_offset_ms  # Subtract offset to start from 0
        current_block.append(word)
        current_word_timings.append((word, ms, ms + 400))  # Default 400ms per word
        
        # Create subtitle block every 2-3 words
        if (len(current_block) >= 3 or 
            word.endswith(('.', '।', '?', '!')) or
            i == len(matches) - 1):
            
            block_start = current_word_timings[0][1]
            block_end = current_word_timings[-1][2]
            
            # Build highlighted text
            highlighted_text = build_highlighted_text(current_word_timings)
            
            subtitle_blocks.append({
                'start': block_start,
                'end': block_end,
                'text': highlighted_text
            })
            
            current_block = []
            current_word_timings = []
    
    # Write ASS file
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(create_ass_header())
        
        for block in subtitle_blocks:
            line = f"Dialogue: 0,{ms_to_ass_time(block['start'])},{ms_to_ass_time(block['end'])},EnhancedSub,,0,0,0,,{block['text']}\n"
            f.write(line)
    
    print(f"Converted {len(subtitle_blocks)} enhanced subtitle blocks to {output_file}")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python text_to_enhanced_ass.py input.txt output.ass")
        sys.exit(1)
    
    convert_text_to_enhanced_ass(sys.argv[1], sys.argv[2])