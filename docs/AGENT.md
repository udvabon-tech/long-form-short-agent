# AI Agent Instructions: Automated Bengali Podcast Reel Creation Pipeline

**Complete autonomous workflow for creating professional Bengali reels from podcast videos**

---

## Overview

This agent autonomously processes Bengali podcast videos and creates multiple vertical reels (608x1080 or 1080x1920) with professional hardburned subtitles, ready for Facebook Reels/Instagram upload.

---

## Prerequisites & Dependencies

### Required Software

```bash
# 1. Python 3.8+ with pip
python3 --version

# 2. FFmpeg (for video/audio processing)
brew install ffmpeg  # macOS
# OR
sudo apt install ffmpeg  # Linux

# 3. FFprobe (usually comes with FFmpeg)
ffprobe -version

# 4. Python packages
pip install google-generativeai>=0.8.0
```

### Required Files

1. **Scripts/text_to_enhanced_ass.py** - Subtitle generation script
   - Located in shared Scripts/ folder
   - Generates ASS subtitle files with Bengali font support
   - Used by all projects

2. **Source video file** (provided by user)
   - Format: `.mp4`, `.mkv`, or any FFmpeg-supported format
   - Can be horizontal or vertical
   - Place in project's Source/ folder

### Environment Setup (New Project)

```bash
# Navigate to main directory
cd "/Users/Adnan/Desktop/Long Form to Shorts"

# Create new project
PROJECT="My_Podcast_Name"
mkdir -p "Projects/$PROJECT"/{Source,Transcripts,Analysis,Processing,Output}

# Add your source video
cp ~/path/to/podcast.mp4 "Projects/$PROJECT/Source/"

# Install Python dependencies (one-time setup)
pip install -r requirements.txt

# Set Gemini API key (for transcription)
export GEMINI_API_KEY="your_api_key_here"

# Verify FFmpeg installation
ffmpeg -version
```

---

## Complete Automated Workflow

### User Input Required:
- **Project name** (e.g., `AI_Podcast_Oct2025`)
- **Video file** (placed in `Projects/[ProjectName]/Source/`)
- **Gemini API key** (for transcription)

### Agent Performs Automatically:

---

## STEP 1: Audio Extraction

**Purpose:** Extract audio from video for transcription

**Command:**
```bash
# From project directory
cd "Projects/$PROJECT"
ffmpeg -i Source/podcast.mp4 -vn -acodec libmp3lame -q:a 2 -t 1800 Transcripts/audio_30min.mp3
```

**Output:** `Projects/$PROJECT/Transcripts/audio_30min.mp3`

**Verification:**
```bash
ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 Transcripts/audio_30min.mp3
```

---

## STEP 2: Audio Transcription with Timestamps

**Purpose:** Generate detailed Bengali transcription with millisecond-precision timestamps

**Script:** Use `Scripts/transcribe_audio_v2.py`

**Process:**
1. Read audio file as binary
2. Send to Gemini 2.5 Pro API with detailed prompt
3. Request format: `[HH:MM:SS.mmm] Speaker N: Bengali text`
4. Save to project's Transcripts folder

**Command:**
```bash
# From main directory
cd "/Users/Adnan/Desktop/Long Form to Shorts"
export GEMINI_API_KEY="your-key-here"
python3 Scripts/transcribe_audio_v2.py "Projects/$PROJECT/Transcripts/audio_30min.mp3"
```

**Python Code (in Scripts/transcribe_audio_v2.py):**
```python
import google.generativeai as genai

genai.configure(api_key=GEMINI_API_KEY)

with open('Projects/$PROJECT/Transcripts/audio_30min.mp3', 'rb') as f:
    audio_data = f.read()

model = genai.GenerativeModel('gemini-2.5-pro')

prompt = """Please transcribe this audio file completely and accurately with detailed timestamps. The audio is in Bangla (Bengali) language.

Requirements:
- Provide complete transcription of all spoken content in Bangla script (বাংলা)
- Include very detailed timestamps for each speaker segment in the format [HH:MM:SS.mmm] at the beginning of each line or phrase
- Use millisecond precision (e.g., [00:00:15.500])
- Add timestamps frequently throughout the conversation, ideally every few seconds or when the speaker changes
- Maintain proper punctuation and formatting
- If there are multiple speakers, indicate speaker changes with labels (Speaker 1, Speaker 2, etc.)
- Preserve the original meaning and context

Format example:
[00:00:00.000] Speaker 1: [Bangla text here]
[00:00:15.500] Speaker 2: [Bangla text here]
[00:00:23.750] Speaker 1: [Bangla text continues]

Transcription:"""

response = model.generate_content([
    prompt,
    {'mime_type': 'audio/mpeg', 'data': audio_data}
])

with open('Projects/$PROJECT/Transcripts/audio_30min_transcription.txt', 'w', encoding='utf-8') as f:
    f.write(response.text)
```

**Output:** `Projects/$PROJECT/Transcripts/audio_30min_transcription.txt` (full transcript with timestamps)

---

## STEP 3: Analyze Transcript and Create Reel Cut Directions

**Purpose:** Identify viral moments and create detailed cut directions for each reel

**Process:**
1. Read full transcript from project's Transcripts folder
2. Analyze for:
   - Hook types (Shock/Fear, Mind-Blowing Stats, Time-Saving, etc.)
   - Viral potential moments
   - Natural conversation breaks
   - Duration (30-90 seconds ideal)
3. Create comprehensive cut directions in project's Analysis folder

**Command:**
```bash
# From main directory
cd "/Users/Adnan/Desktop/Long Form to Shorts"
python3 Scripts/analyze_transcript.py
# Edit script to point to: Projects/$PROJECT/Transcripts/audio_30min_transcription.txt
```

**Output Format:**
```markdown
## REEL #1: "Hook Title in Bengali"
**Hook Type:** Mind-Blowing Stat
**Topic:** AI processing power
**Duration:** ~75 seconds
**Viral Potential:** ⭐⭐⭐⭐⭐

### CUT INSTRUCTIONS:
START: [03:27.177]
END: [04:21.017]

Key Quote: "জেমিনাই, ও হচ্ছে একসাথে দশ লাখ শব্দ প্রসেস করতে পারে।"

Opening Hook: "আপনি এই এআই টুলগুলা যেমন ধরেন জেমিনাই..."

**Content Flow:**
- Gemini can process 10 lakh words at once
- Comparison to normal book (80,000 words)
- Business data analysis example
- Instant decision making capability

**Editing Notes:**
- Emphasize "দশ লাখ শব্দ" visually
- Show shock reaction at [03:34.637]
- Highlight data processing speed
```

**Output:** `Projects/$PROJECT/Analysis/REEL_CUT_DIRECTIONS.md`

---

## STEP 4: Create Individual Reels (Loop Through Each)

For each reel in cut directions, perform the following steps:

### STEP 4.1: Extract Video Segment

**Purpose:** Cut specific time range from source video and convert to vertical format

**Determine Video Dimensions First:**
```bash
# Get source video dimensions
cd "Projects/$PROJECT"
ffprobe -v error -select_streams v:0 -show_entries stream=width,height -of csv=p=0 Source/podcast.mp4
```

**For Horizontal Video (e.g., 1280x720):**
```bash
# Extract and scale to 608x1080 vertical
ffmpeg -i Source/podcast.mp4 \
  -ss START_TIME \
  -to END_TIME \
  -vf "scale=608:1080:force_original_aspect_ratio=increase,crop=608:1080" \
  -c:a copy \
  Processing/reelN.mp4
```

**For Already Vertical Video:**
```bash
# Extract and resize to 608x1080
ffmpeg -i Source/podcast.mp4 \
  -ss START_TIME \
  -to END_TIME \
  -vf "scale=608:1080" \
  -c:a copy \
  Processing/reelN.mp4
```

**Time Format:**
- START_TIME: `HH:MM:SS.mmm` (e.g., `00:03:27.177`)
- END_TIME: `HH:MM:SS.mmm` (e.g., `00:04:21.017`)

**Output:** `Projects/$PROJECT/Processing/reelN.mp4` (where N = reel number)

---

### STEP 4.2: Extract Transcript Segment for Reel

**Purpose:** Get Bengali text with timestamps for this specific reel segment

**Python Script:**
```python
import re

def extract_transcript_segment(transcript_file, start_time, end_time):
    """Extract transcript lines for specific time segment"""

    def time_to_seconds(time_str):
        time_str = time_str.strip('[]')
        parts = time_str.split(':')
        if len(parts) == 3:
            return int(parts[0]) * 3600 + int(parts[1]) * 60 + float(parts[2])
        elif len(parts) == 2:
            return int(parts[0]) * 60 + float(parts[1])
        return 0

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
```

---

### STEP 4.3: Create Word-Level Timestamp File

**Recommended:** Drive everything from the new CLI (no manual Python editing required).

```bash
cd "Projects/$PROJECT"

# Direct CLI usage
python ../../Scripts/create_reel_timestamps.py \
  Transcripts/audio_30min_transcription.txt \
  --start "00:15:47.364" \
  --end "00:17:01.374" \
  --output Processing/reel1_words.txt

# Config-driven usage (after filling project_config.json)
python ../../Scripts/create_reel_timestamps.py \
  --config project_config.json \
  --reel-id reel1
```

The script:
- Slices the transcript to the exact window
- Spreads words using the actual transcript timing (no more fixed 400 ms guess)
- Outputs `word [0mXsYYYms]` format → `Processing/reelN_words.txt`

---

### STEP 4.4: Generate TikTok-Style ASS Subtitle File

```bash
cd "Projects/$PROJECT"

# Direct CLI usage
python ../../Scripts/text_to_tiktok_ass.py \
  Processing/reel1_words.txt \
  --output Processing/reel1_tiktok.ass \
  --title "আপনার মস্তিষ্ক অকেজো হচ্ছে?" \
  --video-duration "0:01:14.00"

# Config-driven usage
python ../../Scripts/text_to_tiktok_ass.py \
  Processing/reel1_words.txt \
  --config project_config.json \
  --reel-id reel1
```

Flags worth tweaking:
- `--max-words-per-line` → keep subtitles concise (default 4)
- `--title-duration` → control how long the hook stays on screen (default 5 s)
- `--title-position-y` / `--subtitle-position-y` → adjust safe zones per platform needs

**Arguments:**
1. `Processing/reelN_words.txt` - Input text with word timestamps
2. `Processing/reelN_tiktok.ass` - Output ASS subtitle file
3. `"Short Title"` - 3-5 word Bengali title (appears at top, fixed throughout video)
4. `"H:MM:SS.CC"` - Video duration in ASS format

**What this does:**
- Parses word timestamps from `Processing/reelN_words.txt`
- Creates fixed title at top (68pt, bold, stays entire video)
- Groups words into single-line subtitle events (3-4 words each)
- Applies 68pt Noto Sans Bengali font for maximum readability
- Title position: Top (Y=120px)
- Subtitle position: Bottom (Y=130px from bottom, single line)
- No line wrapping (WrapStyle: 2)

**Output:** `Projects/$PROJECT/Processing/reelN_tiktok.ass`

**ASS File Features:**
- **Title Style:** Noto Sans Bengali, 68pt, bold, fixed at top
- **Subtitle Style:** Noto Sans Bengali, 68pt, bold, single line at bottom
- **Colors:** White text (#FFFFFF) with semi-transparent dark backgrounds
- **Title Duration:** Entire video (fixed)
- **Subtitle Duration:** Changes with speech timing
- **Resolution:** 608x1080 (vertical)

**Title Guidelines (3-5 words max):**
- Use question format for engagement: "কী হবে?", "হচ্ছে?"
- Front-load hook words
- Examples:
  - ✅ "আপনার মস্তিষ্ক অকেজো হচ্ছে?" (4 words)
  - ✅ "AI নিয়ন্ত্রণ হারালে কী হবে?" (5 words)
  - ✅ "সেরা ব্রেইন মাত্র ২৫০০ টাকায়" (5 words)
  - ❌ "AI ব্যবহারে আপনার মস্তিষ্ক কি অকেজো হয়ে যাচ্ছে" (13 words - too long)

**Alternative (Old Multi-line Karaoke Style):**
If you prefer the old colorful karaoke style with multi-line subtitles:
```bash
python3 ../../Scripts/text_to_enhanced_ass.py \
  Processing/reelN_words.txt \
  Processing/reelN_enhanced.ass
```
- Font: 75pt Noto Sans Bengali
- Colors: Green/Red highlights
- Multi-line display
- Word-by-word karaoke effects

---

### STEP 4.5: Hardburn Subtitles to Video

**Purpose:** Permanently embed TikTok-style subtitles into video pixels

**Command:**
```bash
# From project directory
cd "Projects/$PROJECT"

# Hardburn TikTok-style subtitles (title + single-line)
ffmpeg -i Processing/reelN.mp4 \
  -vf "ass=Processing/reelN_tiktok.ass" \
  -c:a copy \
  "Output/Final_রিল_শিরোনাম.mkv"
```

**What this does:**
1. Reads `Processing/reelN.mp4` frame by frame
2. Renders TikTok-style ASS subtitles with all styling:
   - Fixed title at top (68pt, bold)
   - Single-line subtitles at bottom (68pt, bold)
   - Proper Bengali text rendering with HarfBuzz
   - Semi-transparent dark backgrounds for readability
3. Burns Bengali text permanently onto video pixels
4. Re-encodes video with subtitles as part of the image
5. Keeps audio stream as-is (copy codec)

**Output:** `Projects/$PROJECT/Processing/reelN_huge_font.mkv`

**Important:** Subtitles are now permanently part of the video and cannot be removed or edited.

---

### STEP 4.6: Add Title Overlay (Hook Text)

**Purpose:** Add the reel title as an overlay at the top to instantly hook viewers

**⚠️ CRITICAL: Use ASS Subtitles for Title Overlay**
Bengali text requires proper text shaping (HarfBuzz) which is only available through the ASS subtitle filter.
Using drawtext filter causes broken Bengali characters (vowel signs detach from consonants).

**Extract title from REEL_CUT_DIRECTIONS.md:**
- Get the main title from reel heading (e.g., "এআই দশ লাখ শব্দ একসাথে প্রসেস করতে পারে")
- Short titles (≤6 words): Use single line
- Long titles: Split into 2 lines for better readability on mobile

**STEP 1: Create ASS File for Title Overlay**

**For Single-Line Titles (≤6 words):**
```bash
# Create title_overlay.ass file
cat > title_overlay.ass << 'EOF'
[Script Info]
ScriptType: v4.00+
PlayResX: 608
PlayResY: 1080

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Title,Noto Sans Bengali,42,&H00FFFFFF,&H000000FF,&H00000000,&H00000000,0,0,0,0,100,100,0,0,3,3,0,8,20,20,1020,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
Dialogue: 0,0:00:00.00,0:00:05.00,Title,,0,0,0,,{\pos(304,60)\an2\bord5\3c&H000000&\4a&H55&}YOUR_BENGALI_TITLE_HERE
EOF
```

**For Multi-Line Titles (>6 words):**
```bash
# Create title_overlay.ass file with two lines
cat > title_overlay.ass << 'EOF'
[Script Info]
ScriptType: v4.00+
PlayResX: 608
PlayResY: 1080

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Title,Noto Sans Bengali,38,&H00FFFFFF,&H000000FF,&H00000000,&H00000000,0,0,0,0,100,100,0,0,3,3,0,8,20,20,1020,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
Dialogue: 0,0:00:00.00,0:00:05.00,Title,,0,0,0,,{\pos(304,40)\an2\bord5\3c&H000000&\4a&H55&}LINE_1_HERE
Dialogue: 0,0:00:00.00,0:00:05.00,Title,,0,0,0,,{\pos(304,90)\an2\bord5\3c&H000000&\4a&H55&}LINE_2_HERE
EOF
```

**STEP 2: Apply ASS Title to Video**
```bash
# From project directory
cd "Projects/$PROJECT"

# Use ASS filter (ensures proper Bengali text shaping with HarfBuzz)
ffmpeg -y -i Processing/reelN_huge_font.mkv \
  -vf "ass=Processing/title_overlay_reelN.ass" \
  -c:a copy \
  "Output/[BENGALI_TITLE].mkv"
```

**ASS Parameters Explained:**

**Style Definition:**
- `Fontname: Noto Sans Bengali` - Font that supports proper Bengali rendering
- `Fontsize: 42` (single line) or `38` (multi-line) - Optimal for mobile
- `PrimaryColour: &H00FFFFFF` - White text
- `BorderStyle: 3` - Opaque box background
- `Outline: 3` - Border thickness
- `Shadow: 0` - No shadow
- `Alignment: 8` - Top center alignment

**Dialogue Tags:**
- `\pos(304,60)` - Position (X=304 centers horizontally, Y=60 from top)
- `\an2` - Alignment anchor (bottom-center of text)
- `\bord5` - Border/outline width
- `\3c&H000000&` - Border color (black)
- `\4a&H55&` - Shadow transparency (85% opaque black background)

**Timing:**
- `Start: 0:00:00.00` - Show from beginning
- `End: 0:00:05.00` - Hide after 5 seconds

**⚠️ WHY ASS Instead of Drawtext:**
```
drawtext filter: ❌ Broken Bengali (vowel signs detach: পড়বে → পড়বএ)
ass filter:      ✅ Perfect Bengali (uses HarfBuzz text shaping: পড়বে ✓)

The ASS subtitle filter uses libass with HarfBuzz support, which properly
handles complex Bengali script shaping, conjuncts, and vowel positioning.
```

**⚠️ CRITICAL: Font Requirements:**
- Font MUST be "Noto Sans Bengali" in ASS Style line
- System will auto-find: `/Users/Adnan/Library/Fonts/NotoSansBengali-VariableFont_wdth,wght.ttf`
- FFmpeg with libass + HarfBuzz ensures proper rendering
- Never use drawtext filter for Bengali text

**Output:** `Projects/$PROJECT/Output/[BENGALI_TITLE].mkv` (FINAL UPLOAD-READY VIDEO)

---

### STEP 4.7: Verify Reel Creation

**Check video properties:**
```bash
# From project directory
cd "Projects/$PROJECT"

# Verify dimensions, duration, codecs
ffprobe -v error \
  -show_entries format=duration \
  -show_entries stream=width,height,codec_name \
  -of default=noprint_wrappers=1 \
  "Output/[BENGALI_TITLE].mkv"

# Expected output:
# codec_name=h264
# width=608
# height=1080
# codec_name=aac
# duration=53.840000
```

---

## STEP 5: Organize Output Files

**All files are already organized in project-based structure:**

```bash
# Project structure (already organized):
Projects/$PROJECT/
├── Source/         # Original video
├── Transcripts/    # Audio + transcription
├── Analysis/       # AI analysis + cut directions
├── Processing/     # Intermediate files (can delete after completion)
└── Output/         # ✅ FINAL REELS (ready to upload)

# Final reels are named with Bengali titles:
# Example: Output/আপনার_ব্রেইনে_জং_পড়বে.mkv
```

**Optional: Create project summary:**
```bash
# From project directory
cd "Projects/$PROJECT"

cat > PROJECT_SUMMARY.md << EOF
# Project: $PROJECT

Created: $(date)
Source: Source/podcast.mp4
Total Reels: 3
Format: 608x1080 vertical MKV
Subtitles: Hardburned Bengali (75pt Noto Sans)
Title Overlay: 5-second hook at top (42pt Bengali font)

## Reels Created:
1. Output/[REEL_1_TITLE].mkv
2. Output/[REEL_2_TITLE].mkv
3. Output/[REEL_3_TITLE].mkv

Ready for: Facebook Reels, Instagram Reels, YouTube Shorts
EOF
```

---

## Complete File Structure Example

After processing, project directory should look like:

```
Long Form to Shorts/
├── Scripts/                               # Shared scripts (all projects)
│   ├── transcribe_audio_v2.py
│   ├── text_to_enhanced_ass.py
│   ├── analyze_transcript.py
│   └── create_reel_timestamps.py
│
├── Templates/                             # Shared templates
│   └── title_overlay_template.ass
│
└── Projects/
    └── AI_Podcast_Rokomari_2025/          # Example project
        │
        ├── Source/                        # Original video
        │   └── podcast.mp4
        │
        ├── Transcripts/                   # Audio & transcription
        │   ├── audio_30min.mp3
        │   └── audio_30min_transcription.txt
        │
        ├── Analysis/                      # AI analysis results
        │   ├── REEL_CUT_DIRECTIONS.md
        │   └── REELS_SUMMARY.md
        │
        ├── Processing/                    # Intermediate files
        │   ├── reel1.mp4
        │   ├── reel1_words.txt
        │   ├── reel1_enhanced.ass
        │   ├── reel1_tiktok.ass
        │   ├── reel1_huge_font.mkv
        │   ├── title_overlay_reel1.ass
        │   └── [...same for reel2, reel3]
        │
        └── Output/                        # ✅ FINAL REELS (upload-ready)
            ├── আপনার_ব্রেইনে_জং_পড়বে.mkv
            ├── AI_যখন_নিয়ন্ত্রণের_বাইরে_যাবে.mkv
            └── বিশ্বের_সেরা_ব্রেইন_চাকরি.mkv
```

**Naming Convention:**
- Final reel files named with Bengali title (spaces → underscores)
- Format: `[Bengali_Title].mkv`
- Example: "আপনার ব্রেইনে জং পড়বে!" → `আপনার_ব্রেইনে_জং_পড়বে.mkv`
- Each project is self-contained in its own folder

---

## Agent Execution Checklist

When user provides video file, agent should:

- [ ] **Step 0:** Create project folder structure → `Projects/$PROJECT/{Source,Transcripts,Analysis,Processing,Output}`
- [ ] **Step 1:** Extract audio from video → `Projects/$PROJECT/Transcripts/audio_30min.mp3`
- [ ] **Step 2:** Transcribe audio with Gemini API → `Projects/$PROJECT/Transcripts/audio_30min_transcription.txt`
- [ ] **Step 3:** Analyze transcript and create cut directions → `Projects/$PROJECT/Analysis/REEL_CUT_DIRECTIONS.md`
- [ ] **Step 4:** For each reel (loop through all):
  - [ ] 4.1: Extract video segment → `Processing/reelN.mp4`
  - [ ] 4.2: Confirm transcript window + metadata (timestamps, title, config entry)
  - [ ] 4.3: Create word-level timestamps → `Processing/reelN_words.txt`
  - [ ] 4.4: Generate ASS subtitle file → `Processing/reelN_tiktok.ass` (or `reelN_enhanced.ass` for karaoke style)
  - [ ] 4.5: Hardburn subtitles → `Processing/reelN_huge_font.mkv`
  - [ ] 4.6: Add title overlay → `Output/[BENGALI_TITLE].mkv` ✅
  - [ ] 4.7: Verify output dimensions and duration
- [ ] **Step 5:** All reels saved in project's `Output/` folder with Bengali titles
- [ ] **Step 6:** Report summary to user with project location

---

## Expected Output Summary

**Agent provides to user:**

```
✅ Processing Complete!

Project: AI_Podcast_Rokomari_2025
Location: Projects/AI_Podcast_Rokomari_2025/

Source Video: Source/podcast.mp4 (1280x720, 01:20:48)
Audio Extracted: Transcripts/audio_30min.mp3 (30:00 duration)
Transcription: Transcripts/audio_30min_transcription.txt (500+ lines)
Analysis: Analysis/REEL_CUT_DIRECTIONS.md (3 reels identified)

Created Reels:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
REEL #1: "আপনার ব্রেইনে জং পড়বে!"
  ├─ Duration: 00:01:22.92
  ├─ Format: 608x1080 vertical MKV
  ├─ Subtitles: Hardburned Bengali (75pt)
  ├─ Title Overlay: 5-second hook at top (42pt)
  ├─ Viral Potential: ⭐⭐⭐⭐⭐
  └─ File: Output/আপনার_ব্রেইনে_জং_পড়বে.mkv (9.8 MB) ✅

REEL #2: "এআই দশ লাখ শব্দ একসাথে প্রসেস করতে পারে"
  ├─ Duration: 00:00:53.84
  ├─ Format: 608x1080 vertical MKV
  ├─ Subtitles: Hardburned Bengali (75pt)
  ├─ Title Overlay: 5-second hook at top
  └─ File: Output/এআই_দশ_লাখ_শব্দ_একসাথে_প্রসেস_করতে_পারে.mkv (7.0 MB) ✅

[...more reels if multiple...]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Total Reels Created: 3
Total Output Size: 18.6 MB
Format: MKV with H.264 video + AAC audio
Naming: Bengali title with underscores (spaces replaced)
Ready for Upload: Facebook Reels, Instagram Reels, YouTube Shorts

All reels located in: Projects/AI_Podcast_Rokomari_2025/Output/
Project is self-contained and organized
```

---

## Troubleshooting Guide

### Issue: FFmpeg not found
**Solution:**
```bash
# macOS
brew install ffmpeg

# Linux
sudo apt update && sudo apt install ffmpeg

# Verify
ffmpeg -version
```

### Issue: Gemini API error "ragStoreName"
**Solution:** Use inline audio data method (not file upload):
```python
# Don't use genai.upload_file()
# Instead read file and pass directly:
with open('audio.mp3', 'rb') as f:
    audio_data = f.read()
response = model.generate_content([prompt, {'mime_type': 'audio/mpeg', 'data': audio_data}])
```

### Issue: ASS subtitles not showing
**Solution:** Use absolute path and proper escaping:
```bash
abs_path=$(realpath reelN_enhanced.ass)
ffmpeg -i reelN.mp4 -vf "ass='${abs_path}'" -c:a copy output.mkv
```

### Issue: Bengali text showing as squares
**Solution:** Ensure `text_to_enhanced_ass.py` specifies correct font:
```python
# In ASS file, must have:
Style: Default,Noto Sans Bengali,75,&H00FFFFFF,&H000000FF,&H00000000,&H00000000,0,0,0,0,100,100,0,0,1,2,0,2,10,10,240,1
```

### Issue: Video dimensions invalid
**Solution:** Check source dimensions first:
```bash
ffprobe -v error -select_streams v:0 -show_entries stream=width,height -of csv=p=0 INPUT_VIDEO.mp4

# Then choose appropriate scaling method
# If source width < 608, use: scale=608:-1
# If source height < 1080, use: scale=-1:1080
```

### Issue: Transcription missing timestamps
**Solution:** Ensure prompt explicitly requests millisecond precision:
```
"Include very detailed timestamps for each speaker segment in the format [HH:MM:SS.mmm]"
```

---

## Performance Tips

1. **Parallel Processing:** Process multiple reels simultaneously:
```bash
# Extract all video segments first (fast)
for i in {1..11}; do
    ffmpeg -i source.mp4 -ss START -to END reel${i}.mp4 &
done
wait

# Then process subtitles sequentially (needs order)
for i in {1..11}; do
    python3 text_to_enhanced_ass.py reel${i}.txt reel${i}_enhanced.ass
    ffmpeg -i reel${i}.mp4 -vf "ass=reel${i}_enhanced.ass" reel${i}_huge_font.mkv
done
```

2. **Use FFmpeg hardware acceleration:**
```bash
# macOS (VideoToolbox)
ffmpeg -hwaccel videotoolbox -i input.mp4 ...

# Linux (VAAPI)
ffmpeg -hwaccel vaapi -i input.mp4 ...
```

3. **Reduce subtitle rendering time:**
- Use smaller font during testing (change 75 to 50 in `text_to_enhanced_ass.py`)
- Test with first 10 seconds only: `-ss 0 -t 10`

---

## Quality Checklist for Each Reel

Before marking reel as complete, verify:

✅ **Video Quality:**
- [ ] Resolution is 608x1080 or 1080x1920
- [ ] Duration matches cut directions (±1 second tolerance)
- [ ] No black bars on sides/top/bottom
- [ ] Video plays smoothly without stuttering

✅ **Subtitle Quality:**
- [ ] All Bengali text is readable and properly rendered
- [ ] Font size is large enough for mobile viewing (75pt)
- [ ] Subtitles appear at correct times (synced with audio)
- [ ] Word-by-word highlighting works (karaoke effect)
- [ ] Blue emphasis appears every 4th word
- [ ] Subtitles positioned correctly (240px from bottom)
- [ ] No overlapping or cutoff text

✅ **Audio Quality:**
- [ ] Audio is clear and in sync with video
- [ ] Volume levels are consistent
- [ ] No audio distortion or clipping

✅ **File Format:**
- [ ] File format is MKV or MP4
- [ ] File size is reasonable (5-15 MB for 60 seconds)
- [ ] Compatible with social media platforms

---

## Final Notes for AI Agent

### Critical Points:
1. **Always use UTF-8 encoding** for Bengali text files
2. **Calculate time offset** - video must start at 00:00:00.000, not original timestamp
3. **Use exact FFmpeg commands** as specified (don't modify filter syntax)
4. **Hardburn is permanent** - cannot edit subtitles after this step
5. **Verify each step** before proceeding to next
6. **Keep intermediate files** for debugging (txt, ass, mp4)

### Error Recovery:
- If any step fails, log the error and continue with next reel
- Save progress after each reel completion
- Create error log: `errors.log` with timestamps and descriptions

### User Communication:
- Update user after each major step completion
- Show progress: "Processing Reel 3/11..."
- Estimate time remaining based on video duration
- Provide clear file paths for all outputs

---

## Success Criteria

Pipeline is successful when:
1. Project folder structure created correctly
2. All reels extracted and created without errors
3. Every reel has hardburned Bengali subtitles
4. All videos are 608x1080 or 1080x1920 vertical format
5. Subtitle timing is accurate (±200ms tolerance)
6. All final videos are in project's `Output/` folder
7. File naming uses Bengali titles with underscores
8. Total processing time < 5 minutes per reel

---

**Generated:** 2025-10-16
**Updated:** 2025-10-19
**Version:** 2.0 (Project-Based)
**Compatible with:** FFmpeg 7.x, Python 3.8+, Gemini 2.5 Pro API
**Optimized for:** Bengali podcast content, Facebook Reels, Instagram Reels

---

**This guide enables complete autonomous reel creation from a single video input. Agent should follow steps sequentially and verify output at each stage.**
