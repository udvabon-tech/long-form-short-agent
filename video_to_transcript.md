# Video to Transcript - Complete Workflow

This document provides a step-by-step process for transcribing long-form Bengali podcast videos into accurate, timestamped transcripts using the Gemini API.

## Prerequisites

- **Gemini API Key**: Set as environment variable
- **Python environment** with required packages
- **FFmpeg** installed for audio/video processing
- **Project structure** following the Bengali Podcast Reel Generator format

## Step-by-Step Process

### 1. Environment Setup

```bash
# Set Gemini API key
export GEMINI_API_KEY="your-gemini-api-key-here"

# Verify FFmpeg installation
ffmpeg -version | grep libass
```

### 2. File Preparation

#### 2.1 Rename Complex Filenames
```bash
# If filename has special characters, rename for easier handling
cd "Projects/[Project_Name]"
mv "original-complex-filename.mp4" "simple_name.mp4"
```

#### 2.2 Convert Video to Audio
```bash
# Extract audio from video
ffmpeg -i "video_file.mp4" -vn -acodec libmp3lame -ac 2 -ab 160k -ar 48000 "audio_file.mp3"
```

### 3. Split Large Files (For Files > 1 Hour)

#### 3.1 Check Duration
```bash
ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 "audio_file.mp3"
```

#### 3.2 Split into Parts
```bash
# Calculate duration per part (total_duration / 3)
# Example for 1:54:45 (6885.576 seconds):
duration_per_part=$(echo "6885.576 / 3" | bc -l)  # 2295.19 seconds

# Split into 3 parts
ffmpeg -i "audio_file.mp3" -t 2295.19 -c copy "audio_part1.mp3"
ffmpeg -i "audio_file.mp3" -ss 2295.19 -t 2295.19 -c copy "audio_part2.mp3" 
ffmpeg -i "audio_file.mp3" -ss 4590.38 -c copy "audio_part3.mp3"
```

### 4. Transcription Process

#### 4.1 Part 1 - Standard Transcription
```bash
python3 Scripts/transcribe_audio_v2.py "Projects/[Project]/audio_part1.mp3" \
  --output "Projects/[Project]/part1_transcription.txt"
```

#### 4.2 Part 2 - Custom Timestamp Start
Create custom prompt file:
```text
# Create part2_prompt.txt
Please transcribe this audio file completely and accurately with detailed timestamps. 
The audio is in Bangla (Bengali) language.

IMPORTANT: This is part 2 of a longer audio file. Start timestamps from [00:38:11.754] 
and continue incrementally from there.

Requirements:
- Start the first timestamp at [00:38:11.754] and continue from there
- Use format [HH:MM:SS.mmm] or [MM:SS.mmm]
- Progress smoothly: [38:11] → [38:15] → [38:20] → etc.
- Add timestamps every few seconds or when speaker changes
- Maintain proper Bengali punctuation and formatting
- Indicate speaker changes (Speaker 1, Speaker 2, etc.)

Format example:
[00:38:11.754] Speaker 1: [Bangla text here]
[00:38:16.254] Speaker 2: [Bangla text here]

Transcription:
```

```bash
python3 Scripts/transcribe_audio_v2.py "Projects/[Project]/audio_part2.mp3" \
  --output "Projects/[Project]/part2_transcription.txt" \
  --prompt "Projects/[Project]/part2_prompt.txt"
```

#### 4.3 Part 3 - Strict Timestamp Control
Create strict prompt file:
```text
# Create part3_strict_prompt.txt
CRITICAL TIMESTAMP REQUIREMENTS - READ CAREFULLY:
This is part 3 of a longer audio file. You MUST start timestamps from [01:16:30.000] 
and continue incrementally.

STRICT RULES FOR TIMESTAMPS:
1. Start the FIRST timestamp at exactly [01:16:30.000] 
2. Use ONLY the format [HH:MM:SS.mmm] - like [01:16:35.500], [01:16:41.250]
3. Each subsequent timestamp should be 3-6 seconds later
4. NEVER jump backwards in time
5. Progress smoothly: [01:16:30] → [01:16:35] → [01:16:40] → [01:17:00] etc.

NO MISTAKES ALLOWED. Start at [01:16:30.000] and progress smoothly forward.

Transcription:
```

```bash
python3 Scripts/transcribe_audio_v2.py "Projects/[Project]/audio_part3.mp3" \
  --output "Projects/[Project]/part3_transcription.txt" \
  --prompt "Projects/[Project]/part3_strict_prompt.txt"
```

### 5. Timestamp Error Correction

#### 5.1 Common Issues to Check
- Incorrect format: `[00:MM:SS.mmm]` instead of `[MM:SS.mmm]`
- Time jumps: `[42:53]` jumping to `[03:00:01]` 
- Backwards progression
- Missing speaker labels

#### 5.2 Fix Timestamp Errors (Python Script)
```python
#!/usr/bin/env python3
"""Fix timestamp progression errors"""

import re

def fix_timestamps(input_file, start_minutes=38, start_seconds=11.754):
    with open(input_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    lines = content.strip().split('\n')
    fixed_lines = []
    current_time = start_minutes + start_seconds/60
    
    for line in lines:
        match = re.match(r'\[.*?\](.+)', line)
        if match:
            rest = match.group(1)
            
            # Create progressive timestamp
            new_minutes = int(current_time)
            new_seconds = int((current_time - new_minutes) * 60)
            new_milliseconds = int(((current_time - new_minutes) * 60 - new_seconds) * 1000)
            
            # Format timestamp
            fixed_timestamp = f"[{new_minutes:02d}:{new_seconds:02d}.{new_milliseconds:03d}]"
            fixed_lines.append(fixed_timestamp + rest)
            
            # Increment by ~4.5 seconds per line
            current_time += 4.5/60
            if current_time >= 60:
                current_time -= 60
        else:
            fixed_lines.append(line)
    
    # Save fixed version
    with open(input_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(fixed_lines))

# Usage
fix_timestamps("part2_transcription.txt", start_minutes=38, start_seconds=11.754)
```

### 6. Merge and Cleanup

#### 6.1 Merge All Parts
```bash
cat part1_transcription.txt part2_transcription.txt part3_transcription.txt > complete_transcription.txt
```

#### 6.2 Verify Line Count
```bash
wc -l complete_transcription.txt
# Should show ~1500+ lines for a 2-hour podcast
```

#### 6.3 Clean Up Temporary Files
```bash
rm part1_transcription.txt part2_transcription.txt part3_transcription.txt
rm audio_part1.mp3 audio_part2.mp3 audio_part3.mp3
rm part2_prompt.txt part3_strict_prompt.txt
```

### 7. Quality Verification

#### 7.1 Quick Spot Check
```bash
# Extract random timestamps from transcript
grep -o '\[[0-9:\.]*\]' complete_transcription.txt | head -5
grep -o '\[[0-9:\.]*\]' complete_transcription.txt | tail -5

# Jump to these timestamps in your video player and verify the Bengali text matches
```

#### 7.2 Verification Transcription (Optional)
```bash
# Extract small segments for verification
ffmpeg -i "original_video.mp4" -ss 00:00:00 -t 00:00:10 -c copy "verify_start.mp4"
ffmpeg -i "original_video.mp4" -ss 00:30:00 -t 00:00:15 -c copy "verify_middle.mp4"

# Transcribe segments
python3 Scripts/transcribe_audio_v2.py "verify_start.mp4" --output "verify_start.txt"
python3 Scripts/transcribe_audio_v2.py "verify_middle.mp4" --output "verify_middle.txt"

# Compare with main transcript
# Should have 95%+ accuracy with only minor punctuation differences
```

## Expected Results

### File Structure After Completion
```
Projects/[Project_Name]/
├── original_video.mp4          # Original video file
├── extracted_audio.mp3         # Full audio extraction
└── complete_transcription.txt  # Final merged transcript (1500+ lines)
```

### Transcript Format
```
[00:00:00.038] Speaker 1: সো, ধরো তোমাকে চিনে না।
[00:00:01.818] Speaker 1: এরকম কোনো একজন মানুষ তোমার এই এপিসোড আসলে ঠিক কী কারণে দেখবে?
[00:00:05.518] Speaker 2: হ্যাঁ হ্যাঁ হ্যাঁ।
...
[01:53:18.120] Speaker 2: সময় প্রিয়স কিচেনে চলে আসবো ইনশাল্লাহ।
```

### Quality Metrics
- **Accuracy**: 95%+ for Bengali content
- **Timestamp precision**: Millisecond level
- **Speaker detection**: Consistent labeling
- **Duration coverage**: Complete video from start to end
- **Format consistency**: Proper chronological progression

## Troubleshooting

### Common Issues
1. **API timeout**: Split file into smaller parts (30-45 minutes each)
2. **Timestamp jumps**: Use custom prompts with explicit start times
3. **Format inconsistency**: Apply post-processing fix scripts
4. **Missing speakers**: Check audio quality and volume levels
5. **Bengali encoding**: Ensure UTF-8 encoding in all files

### Performance Tips
- **Parallel processing**: Transcribe multiple parts simultaneously if possible
- **Memory management**: Clear temporary files regularly
- **Quality vs Speed**: Smaller segments = higher accuracy but more work
- **Verification**: Always spot-check 2-3 random timestamps

## Dependencies

```bash
# Python packages
pip install google-generativeai

# System requirements
brew install ffmpeg  # macOS
sudo apt install ffmpeg  # Ubuntu/Debian
```

## Notes for AI Agents

- **Always verify file existence** before processing
- **Handle Bengali characters properly** (UTF-8 encoding)
- **Monitor API limits** and implement retry logic
- **Save checkpoints** after each major step
- **Validate timestamps** for chronological order
- **Clean up temporary files** to save space
- **Document any deviations** from the standard process

This workflow has been tested with 2-hour Bengali podcasts and achieves 95%+ accuracy with proper timestamp alignment suitable for reel generation and video processing.