# Long Form to Shorts - Bengali Podcast Reel Generator

Automated pipeline to extract viral-worthy reels from Bengali podcast videos with professional subtitles and title overlays.

## Features

- **AI-Powered Transcription**: Uses Gemini 2.5 Pro API for accurate Bengali transcription with millisecond-precision timestamps
- **Viral Moment Detection**: AI analysis identifies the most engaging segments
- **Professional Subtitles**: Word-by-word karaoke highlighting with proper Bengali text rendering
- **Title Overlays**: Beautiful Bengali title cards with HarfBuzz text shaping
- **Mobile-Optimized**: Vertical 608x1080 format perfect for Instagram Reels, Facebook Reels, and YouTube Shorts

## Prerequisites

### 1. FFmpeg Installation

**macOS:**
```bash
brew install ffmpeg
```

**Ubuntu/Debian:**
```bash
sudo apt-get install ffmpeg
```

**Windows:**
Download from https://ffmpeg.org/download.html

**Verify Installation:**
```bash
ffmpeg -version
```
Ensure your build includes `--enable-libass` for Bengali text support.

### 2. Python Dependencies

```bash
pip install -r requirements.txt
```

### 3. Gemini API Key

1. Get your API key from https://aistudio.google.com/apikey
2. Set environment variable:

**macOS/Linux:**
```bash
export GEMINI_API_KEY="your-api-key-here"
```

**Windows:**
```cmd
set GEMINI_API_KEY=your-api-key-here
```

### 4. Bengali Font

**macOS:**
- Font is pre-installed: Noto Sans Bengali Variable Font
- Location: `/System/Library/Fonts/Supplemental/Noto Sans Bengali.ttc`

**Linux:**
```bash
sudo apt-get install fonts-noto-bengali
```

**Windows:**
Download from: https://fonts.google.com/noto/specimen/Noto+Sans+Bengali

## Quick Start (Project-Based)

### Step 1: Create Project

```bash
PROJECT="My_Podcast_Name"
mkdir -p "Projects/$PROJECT"/{Source,Transcripts,Analysis,Processing,Output}
```

### Step 2: Add Your Video

```bash
cp ~/path/to/podcast.mp4 "Projects/$PROJECT/Source/"
cd "Projects/$PROJECT"
```

### Step 3: Extract Audio

```bash
ffmpeg -i Source/podcast.mp4 -vn -acodec libmp3lame -q:a 2 -t 1800 Transcripts/audio_30min.mp3
```

### Step 4: Transcribe with Gemini

```bash
cd ../..  # Back to main directory
export GEMINI_API_KEY="your-key"
python Scripts/transcribe_audio_v2.py "Projects/$PROJECT/Transcripts/audio_30min.mp3"
```

This creates `Projects/$PROJECT/Transcripts/audio_30min_transcription.txt` with detailed timestamps.

### Step 4: Analyze for Viral Moments

Ask Gemini to analyze the transcript and identify the best reel-worthy segment. Provide:
- Start timestamp: `[HH:MM:SS.mmm]`
- End timestamp: `[HH:MM:SS.mmm]`
- Bengali title for the reel

### Step 5: Extract Video Segment

```bash
# From project directory
cd "Projects/$PROJECT"
ffmpeg -i Source/podcast.mp4 \
  -ss HH:MM:SS.mmm \
  -to HH:MM:SS.mmm \
  -vf "scale=608:1080:force_original_aspect_ratio=increase,crop=608:1080" \
  -c:a copy \
  Processing/reel1.mp4
```

### Step 6: Create Word-Level Timestamps

```bash
# From main directory
python3 Scripts/create_reel_timestamps.py
```

Edit the script to set:
- Input transcript file (in project's Transcripts/)
- Start and end timestamps
- Output file: `Projects/$PROJECT/Processing/reel1.txt`

### Step 7: Generate ASS Subtitles

```bash
# From project directory
cd "Projects/$PROJECT"
python3 ../../Scripts/text_to_enhanced_ass.py Processing/reel1.txt Processing/reel1_enhanced.ass
```

### Step 8: Hardburn Subtitles

```bash
ffmpeg -i Processing/reel1.mp4 \
  -vf "ass=Processing/reel1_enhanced.ass" \
  -c:a copy \
  Processing/reel1_huge_font.mkv
```

### Step 9: Create Title Overlay

Create `Projects/$PROJECT/Processing/title_overlay.ass`:

```
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
```

Replace `YOUR_BENGALI_TITLE_HERE` with your Bengali title.

### Step 10: Apply Title

```bash
# From project directory
cd "Projects/$PROJECT"
ffmpeg -y -i Processing/reel1_huge_font.mkv \
  -vf "ass=Processing/title_overlay.ass" \
  -c:a copy \
  "Output/YOUR_BENGALI_TITLE_WITH_UNDERSCORES.mkv"
```

**Example:**
```bash
ffmpeg -y -i Processing/reel1_huge_font.mkv \
  -vf "ass=Processing/title_overlay.ass" \
  -c:a copy \
  "Output/আপনার_ব্রেইনে_জং_পড়বে.mkv"
```

## File Naming Convention

Use Bengali title with underscores replacing spaces:
- ✅ `আপনার_ব্রেইনে_জং_পড়বে.mkv`
- ❌ `আপনার ব্রেইনে জং পড়বে.mkv` (spaces cause issues)

## Important Notes

### Bengali Text Rendering

- **Always use ASS subtitles** for Bengali text, never FFmpeg's `drawtext` filter
- `drawtext` doesn't support HarfBuzz text shaping and will break Bengali characters
- Example: পড়বে displayed as পড়বএ (vowel detached)
- ASS filter uses libass + HarfBuzz for proper rendering

### Subtitle Styling

- **Subtitle Font Size**: 75pt (bottom of screen)
- **Title Font Size**: 42pt (top of screen)
- **Title Duration**: 5 seconds
- **Word Highlighting**: Every 4th word in red, others in green

### Video Specifications

- **Resolution**: 608x1080 (vertical)
- **Format**: Mobile-optimized for social media
- **Aspect Ratio**: 9:16

## Troubleshooting

### Broken Bengali Characters

If you see broken Bengali text (vowels detached, conjuncts split):
- **Cause**: Using FFmpeg drawtext filter
- **Solution**: Use ASS subtitle format instead
- Check `AGENT.md` for detailed explanation

### API Key Issues

If transcription fails:
```bash
echo $GEMINI_API_KEY  # Verify key is set
export GEMINI_API_KEY="your-key-here"  # Set if missing
```

### Font Not Found

If font errors occur:
- **macOS**: Use `/System/Library/Fonts/Supplemental/Noto Sans Bengali.ttc`
- **Linux**: Install with `sudo apt-get install fonts-noto-bengali`
- **Windows**: Download and install from Google Fonts

### FFmpeg Not Found

```bash
which ffmpeg  # Check if installed
ffmpeg -version  # Verify libass support
```

## File Organization

This project uses a **project-based structure** where each podcast gets its own folder:

```
Long Form to Shorts/
├── Projects/               # All content projects
│   ├── Project_Name_1/     # Each project is self-contained
│   │   ├── Source/         # Original video
│   │   ├── Transcripts/    # Audio & transcription
│   │   ├── Analysis/       # AI analysis
│   │   ├── Processing/     # Intermediate files
│   │   └── Output/         # Final reels ✅
│   └── Project_Name_2/
├── Scripts/                # Shared automation scripts
└── Templates/              # Shared templates
```

**Create New Project:**
```bash
PROJECT="My_Podcast_Name"
mkdir -p "Projects/$PROJECT"/{Source,Transcripts,Analysis,Processing,Output}
```

See `FILE_ORGANIZATION.md` for:
- Complete project structure
- Project naming conventions
- Managing multiple projects
- Archive and cleanup instructions

## Complete Documentation

See `AGENT.md` for:
- Detailed step-by-step pipeline
- Technical explanations
- Advanced customization options
- Examples and use cases

## Support

For issues or questions:
1. Check `AGENT.md` for detailed documentation
2. Verify all prerequisites are installed
3. Ensure Gemini API key is set correctly
4. Check FFmpeg includes libass support

## License

This tool is for creating social media content from Bengali podcasts. Ensure you have rights to the source material.

---

**Happy Reel Making! 🎬**
