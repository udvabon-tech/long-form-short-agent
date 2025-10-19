# Quick Start Guide - 10 Minutes to Your First Reel

## Prerequisites Checklist

- [ ] FFmpeg installed (`brew install ffmpeg` on macOS)
- [ ] Python 3.7+ installed
- [ ] Gemini API key from https://aistudio.google.com/apikey
- [ ] Noto Sans Bengali font (pre-installed on macOS)

## Setup (One-Time)

```bash
# 1. Install Python dependencies
pip install -r requirements.txt

# 2. Set your Gemini API key
export GEMINI_API_KEY="your-api-key-here"

# 3. Verify FFmpeg
ffmpeg -version
```

## Create Your First Reel (Project-Based)

### 1. Create Project Folder
```bash
# Create a new project with descriptive name
PROJECT="My_Podcast_Name"
mkdir -p "Projects/$PROJECT"/{Source,Transcripts,Analysis,Processing,Output}
```

### 2. Add Your Video
```bash
# Copy your Bengali podcast video to project
cp ~/path/to/your/podcast.mp4 "Projects/$PROJECT/Source/"
cd "Projects/$PROJECT"
```

### 3. Extract Audio
```bash
# Extract first 30 minutes (or full: remove -t 1800)
ffmpeg -i Source/podcast.mp4 -vn -acodec libmp3lame -q:a 2 -t 1800 Transcripts/audio_30min.mp3
```

### 4. Transcribe
```bash
cd ../..  # Back to main directory
export GEMINI_API_KEY="your-key"
python Scripts/transcribe_audio_v2.py "Projects/$PROJECT/Transcripts/audio_30min.mp3"
```
Output: `Projects/$PROJECT/Transcripts/audio_30min_transcription.txt`

### 5. Analyze for Viral Moments
```bash
cd "Projects/$PROJECT"
# Use AI (Claude/Gemini) to analyze Transcripts/audio_30min_transcription.txt
# Identify 3 viral-worthy segments with timestamps
```

### 6. Extract Video Segment
```bash
# Example: Extract from 00:15:47.019 to 00:17:09.919
ffmpeg -i Source/podcast.mp4 \
  -ss 00:15:47.019 \
  -to 00:17:09.919 \
  -vf "scale=608:1080:force_original_aspect_ratio=increase,crop=608:1080" \
  -c:a copy \
  Processing/reel1.mp4
```

### 7. Create Word Timestamps
```bash
# Create script to extract segment and generate timestamps
# Point to: Transcripts/audio_30min_transcription.txt
# Output to: Processing/reel1.txt
python ../../Scripts/create_reel_timestamps.py
```

### 8. Generate Subtitles
```bash
python ../../Scripts/text_to_enhanced_ass.py Processing/reel1.txt Processing/reel1_enhanced.ass
```

### 9. Hardburn Subtitles
```bash
ffmpeg -i Processing/reel1.mp4 \
  -vf "ass=Processing/reel1_enhanced.ass" \
  -c:a copy \
  Processing/reel1_huge_font.mkv
```

### 10. Create & Apply Title
```bash
# Create title overlay (edit with your Bengali title)
cat > Processing/title_overlay.ass << 'EOF'
[Script Info]
ScriptType: v4.00+
PlayResX: 608
PlayResY: 1080

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Title,Noto Sans Bengali,38,&H00FFFFFF,&H000000FF,&H00000000,&H00000000,0,0,0,0,100,100,0,0,3,3,0,8,20,20,1020,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
Dialogue: 0,0:00:00.00,0:00:05.00,Title,,0,0,0,,{\pos(304,60)\an2\bord5\3c&H000000&\4a&H55&}YOUR_BENGALI_TITLE
EOF

# Apply title
ffmpeg -y -i Processing/reel1_huge_font.mkv \
  -vf "ass=Processing/title_overlay.ass" \
  -c:a copy \
  "Output/আপনার_বাংলা_শিরোনাম.mkv"
```

## Done! 🎉

Your final reel is ready: `Projects/$PROJECT/Output/আপনার_বাংলা_শিরোনাম.mkv`

Upload to:
- Instagram Reels
- Facebook Reels
- YouTube Shorts

---

## Example Complete Workflow (Project-Based)

```bash
# Setup (one-time)
pip install -r requirements.txt
export GEMINI_API_KEY="AIzaSyC..."

# Create project
PROJECT="My_Podcast"
mkdir -p "Projects/$PROJECT"/{Source,Transcripts,Analysis,Processing,Output}

# Add video
cp ~/Downloads/podcast.mp4 "Projects/$PROJECT/Source/"
cd "Projects/$PROJECT"

# Extract audio
ffmpeg -i Source/podcast.mp4 -vn -acodec libmp3lame -q:a 2 -t 1800 Transcripts/audio_30min.mp3

# Transcribe
cd ../..
python Scripts/transcribe_audio_v2.py "Projects/$PROJECT/Transcripts/audio_30min.mp3"

# Back to project
cd "Projects/$PROJECT"

# Extract segment (after analyzing transcript)
ffmpeg -i Source/podcast.mp4 \
  -ss 00:15:47.019 -to 00:17:09.919 \
  -vf "scale=608:1080:force_original_aspect_ratio=increase,crop=608:1080" \
  -c:a copy Processing/reel1.mp4

# Create timestamps & subtitles
python ../../Scripts/create_reel_timestamps.py
python ../../Scripts/text_to_enhanced_ass.py Processing/reel1.txt Processing/reel1_enhanced.ass
ffmpeg -i Processing/reel1.mp4 -vf "ass=Processing/reel1_enhanced.ass" -c:a copy Processing/reel1_huge_font.mkv

# Create & apply title
# (Create title_overlay.ass, then:)
ffmpeg -y -i Processing/reel1_huge_font.mkv \
  -vf "ass=Processing/title_overlay.ass" \
  -c:a copy "Output/আপনার_শিরোনাম.mkv"
```

## File Organization (Project-Based)

Each project is self-contained:
```
Projects/My_Podcast/
├── Source/         - Original video
├── Transcripts/    - Audio & transcription
├── Analysis/       - AI analysis results
├── Processing/     - Intermediate files (can delete)
└── Output/         - Final reels ✅
```

See `FILE_ORGANIZATION.md` for complete details.

## Need Help?

See `README.md` for detailed documentation or `AGENT.md` for complete pipeline reference.
