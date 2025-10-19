#!/usr/bin/env python3
"""
Convert multi-line karaoke subtitles to single-line format
Keeps title at top, shows words at bottom on ONE line
"""

import re
import sys

def convert_to_single_line(input_ass, output_ass, title_text, video_duration):
    """
    Convert multi-line subtitles to single line format

    Args:
        input_ass: Original subtitle file with multi-line karaoke
        output_ass: Output file with single-line subtitles
        title_text: Bengali title text to show at top
        video_duration: Duration in format "HH:MM:SS"
    """

    # Read original subtitle file
    with open(input_ass, 'r', encoding='utf-8') as f:
        content = f.read()

    # Extract dialogue lines
    events_section = content.split('[Events]')[1] if '[Events]' in content else content
    dialogues = re.findall(r'Dialogue: (.*)', events_section)

    # Parse each dialogue line
    subtitle_events = []
    for dialogue in dialogues:
        parts = dialogue.split(',', 9)
        if len(parts) >= 10:
            layer = parts[0]
            start = parts[1]
            end = parts[2]
            style = parts[3]
            text = parts[9]

            # Remove karaoke tags and extract clean text
            clean_text = re.sub(r'\{[^}]+\}', '', text).strip()
            if clean_text:
                subtitle_events.append({
                    'start': start,
                    'end': end,
                    'text': clean_text
                })

    # Create new ASS file with title + single-line subtitles
    output_content = f"""[Script Info]
ScriptType: v4.00+
WrapStyle: 0
ScaledBorderAndShadow: yes
PlayResX: 608
PlayResY: 1080

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Title,Noto Sans Bengali,65,&H00FFFFFF,&H000000FF,&H00000000,&HE0000000,-1,0,0,0,100,100,0,0,1,5,0,8,20,20,920,1
Style: OneLine,Noto Sans Bengali,55,&H00FFFFFF,&H000000FF,&H00000000,&HC0000000,-1,0,0,0,100,100,0,0,1,4,0,2,30,30,140,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
Dialogue: 0,0:00:00.00,{video_duration},Title,,0,0,0,,{{\\pos(304,120)\\an2}}{title_text}
"""

    # Add single-line subtitles
    for event in subtitle_events:
        output_content += f"Dialogue: 0,{event['start']},{event['end']},OneLine,,0,0,0,,{event['text']}\n"

    # Write output file
    with open(output_ass, 'w', encoding='utf-8') as f:
        f.write(output_content)

    print(f"✅ Created {output_ass}")
    print(f"   Title: {title_text}")
    print(f"   Subtitle events: {len(subtitle_events)}")


if __name__ == "__main__":
    # Reel 1
    convert_to_single_line(
        'Projects/AI_Podcast_Rokomari_2025/Processing/reel1_enhanced.ass',
        'Projects/AI_Podcast_Rokomari_2025/Processing/reel1_single_line.ass',
        'আপনার মস্তিষ্ক অকেজো হচ্ছে?',
        '0:01:14.00'
    )

    # Reel 2
    convert_to_single_line(
        'Projects/AI_Podcast_Rokomari_2025/Processing/reel2_enhanced.ass',
        'Projects/AI_Podcast_Rokomari_2025/Processing/reel2_single_line.ass',
        'AI নিয়ন্ত্রণ হারালে কী হবে?',
        '0:00:45.00'
    )

    # Reel 3
    convert_to_single_line(
        'Projects/AI_Podcast_Rokomari_2025/Processing/reel3_enhanced.ass',
        'Projects/AI_Podcast_Rokomari_2025/Processing/reel3_single_line.ass',
        'সেরা ব্রেইন মাত্র ২৫০০ টাকায়',
        '0:00:32.00'
    )
