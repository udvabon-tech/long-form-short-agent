# Long Form to Shorts

Convert long-form videos into short-form content (reels/shorts) with automated Bengali subtitles.

## Installation & Setup

### 1. Download Files

You need only these files:
```
your-folder/
├── create_reel.py      # Main script
├── your_video.mp4      # Source video
├── transcript.txt      # Transcript with timestamps
└── README.md          # This documentation (optional)
```

### 2. Install System Requirements

**Python 3.7+** (usually pre-installed)
```bash
python3 --version
```

**FFmpeg** (required for video processing)
```bash
# macOS
brew install ffmpeg

# Ubuntu/Debian
sudo apt update && sudo apt install ffmpeg

# Windows
# Download from https://ffmpeg.org/download.html
```

**Bengali Font** (for subtitle rendering)
```bash
# macOS - usually pre-installed

# Ubuntu/Debian
sudo apt install fonts-noto-bengali

# Windows
# Download Noto Sans Bengali from https://fonts.google.com/noto/specimen/Noto+Sans+Bengali
```

### 3. Verify Installation

```bash
# Check Python
python3 --version

# Check FFmpeg (must include libass for subtitles)
ffmpeg -version | grep libass

# Should show: --enable-libass
```

## Quick Start

### Basic Usage

```bash
python3 create_reel.py video.mp4 transcript.txt "14:21.843" "16:18.063" "Title Text"
```

### Complete Example

```bash
# Create a 30-second reel
python3 create_reel.py \
  my_podcast.mp4 \
  my_transcript.txt \
  "14:21.843" \
  "14:51.843" \
  "AI এর জগৎ" \
  --output "ai_discussion"
```

**What happens:**
1. Script extracts 30-second video segment (14:21.843 to 14:51.843)
2. Generates Bengali subtitles from transcript
3. Creates TikTok-format video (608x1080)
4. Outputs final reel: `Output/ai_discussion.mkv`

## Arguments

- `video.mp4` - Source video file
- `transcript.txt` - Transcript with timestamps (see format below)
- `"14:21.843"` - Start time (MM:SS.mmm or HH:MM:SS.mmm)
- `"16:18.063"` - End time (MM:SS.mmm or HH:MM:SS.mmm)
- `"Title Text"` - Bengali title for overlay
- `--output name` - Optional custom name (default: auto-generated)

## Transcript Format

Your transcript file must have this format:

```
[14:21.843] Speaker 1: কোডেক্স হচ্ছে আপনি একটা কোড বেজ ওকে কানেক্ট করে দিবেন।
[14:25.123] Speaker 2: অনলাইনে যে কোড বেজ রাখে, ওইটাকে বলে হচ্ছে গিটহাব।
[14:28.456] Speaker 1: গিটহাবে সফটওয়্যারের মেইন কোডগুলা থাকে।
```

**Required:**
- Timestamps in `[MM:SS.mmm]` or `[HH:MM:SS.mmm]` format
- Speaker labels (any format)
- Bengali or English text after colon

## Output

**Generated files:**
```
Processing/         # Auto-created temporary files
├── words.txt       # Extracted words with timing
├── subtitles.ass   # Subtitle file
└── segment.mp4     # Video segment

Output/             # Auto-created final output
└── your_reel.mkv   # Final reel (ready for social media)
```

**Video specs:**
- **Resolution:** 608x1080 (TikTok/Instagram format)
- **Subtitles:** Bengali text, 3-4 words per line
- **Title:** Fixed overlay at top
- **Format:** .mkv (works on all platforms)

## Troubleshooting

### "FFmpeg not found"
```bash
# Install FFmpeg first
brew install ffmpeg  # macOS
sudo apt install ffmpeg  # Linux

# Verify installation
ffmpeg -version
```

### "Font not found" or broken Bengali text
```bash
# Linux - install Bengali fonts
sudo apt install fonts-noto-bengali

# macOS - font usually pre-installed
# Windows - download from Google Fonts
```

### "No words found in time range"
- Check transcript file format
- Verify timestamps are correct
- Ensure time range exists in transcript

### Video processing errors
```bash
# Check if video file exists and is readable
ffprobe your_video.mp4

# Verify FFmpeg has libass support (for subtitles)
ffmpeg -version | grep libass
```

## Advanced Usage

### Custom output name
```bash
python3 create_reel.py video.mp4 transcript.txt "5:00" "5:30" "Title" --output "my_reel"
# Creates: Output/my_reel.mkv
```

### Longer segments
```bash
# 2-minute reel
python3 create_reel.py video.mp4 transcript.txt "10:00" "12:00" "দীর্ঘ আলোচনা"
```

### Different timestamp formats
```bash
# Both formats work
python3 create_reel.py video.mp4 transcript.txt "5:30.500" "6:00.750" "Title"  # MM:SS.mmm
python3 create_reel.py video.mp4 transcript.txt "1:05:30.500" "1:06:00.750" "Title"  # HH:MM:SS.mmm
```

## Title Guidelines

**Good titles (3-5 words):**
- ✅ "AI এর ভবিষ্যৎ" (3 words)
- ✅ "আপনার মস্তিষ্ক অকেজো হচ্ছে?" (4 words)
- ✅ "সেরা ব্রেইন মাত্র ২৫০০ টাকায়" (5 words)

**Avoid long titles:**
- ❌ "AI ব্যবহারে আপনার মস্তিষ্ক কি অকেজো হয়ে যাচ্ছে?" (Too long)

## File Organization

**Minimal setup:**
```
your-project/
├── create_reel.py
├── podcast.mp4
├── transcript.txt
├── Processing/    # Auto-created
└── Output/        # Auto-created
```

**Multiple projects:**
```
reels/
├── create_reel.py
├── Project1/
│   ├── video1.mp4
│   ├── transcript1.txt
│   └── Output/
├── Project2/
│   ├── video2.mp4
│   ├── transcript2.txt
│   └── Output/
```

## License

This tool is for creating social media content. Ensure you have rights to the source material.

---

**Need help?** Check that:
1. Python 3.7+ is installed
2. FFmpeg is installed with libass support
3. Bengali fonts are installed
4. Transcript format is correct
5. Video and transcript files exist

**Happy Reel Making! 🎬**