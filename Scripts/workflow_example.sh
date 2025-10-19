#!/bin/bash
# Example Workflow Script for Creating Bengali Reels
# This is a template - edit with your specific values

set -e  # Exit on error

echo "=================================================="
echo "Bengali Podcast to Reel - Automated Workflow"
echo "=================================================="

# CONFIGURATION - EDIT THESE VALUES
INPUT_VIDEO="Input/your_podcast.mp4"
START_TIME="00:15:47.019"
END_TIME="00:17:09.919"
BENGALI_TITLE="আপনার বাংলা শিরোনাম"  # Your Bengali title
OUTPUT_NAME="${BENGALI_TITLE// /_}"  # Replace spaces with underscores

# Check if Gemini API key is set
if [ -z "$GEMINI_API_KEY" ]; then
    echo "❌ Error: GEMINI_API_KEY not set"
    echo "Run: export GEMINI_API_KEY='your-key-here'"
    exit 1
fi

# Check if FFmpeg is installed
if ! command -v ffmpeg &> /dev/null; then
    echo "❌ Error: FFmpeg not installed"
    echo "Install with: brew install ffmpeg (macOS)"
    exit 1
fi

echo ""
echo "📹 Input Video: $INPUT_VIDEO"
echo "⏰ Start: $START_TIME"
echo "⏰ End: $END_TIME"
echo "📝 Title: $BENGALI_TITLE"
echo ""

# Step 1: Extract audio
echo "🎵 Step 1/9: Extracting audio..."
ffmpeg -y -i "$INPUT_VIDEO" -vn -acodec libmp3lame -q:a 2 podcast_audio.mp3
echo "✅ Audio extracted"

# Step 2: Transcribe
echo ""
echo "📝 Step 2/9: Transcribing with Gemini API..."
python Scripts/transcribe_audio_v2.py podcast_audio.mp3
echo "✅ Transcription complete"

# Step 3: Extract video segment
echo ""
echo "✂️  Step 3/9: Extracting video segment..."
ffmpeg -y -i "$INPUT_VIDEO" \
  -ss "$START_TIME" \
  -to "$END_TIME" \
  -vf "scale=608:1080:force_original_aspect_ratio=increase,crop=608:1080" \
  -c:a copy \
  Output/reel1.mp4
echo "✅ Segment extracted"

# Step 4: Create word timestamps
echo ""
echo "⏱️  Step 4/9: Creating word-level timestamps..."
echo "⚠️  Note: Edit Scripts/create_timestamp_text.py with your START_TIME and END_TIME"
echo "Press Enter when ready..."
read
python Scripts/create_timestamp_text.py
echo "✅ Timestamps created"

# Step 5: Generate ASS subtitles
echo ""
echo "📄 Step 5/9: Generating ASS subtitles..."
python Scripts/text_to_enhanced_ass.py Output/reel1.txt Output/reel1_enhanced.ass
echo "✅ Subtitles generated"

# Step 6: Hardburn subtitles
echo ""
echo "🔥 Step 6/9: Hardburning subtitles..."
ffmpeg -y -i Output/reel1.mp4 \
  -vf "ass=Output/reel1_enhanced.ass" \
  -c:a copy \
  Output/reel1_huge_font.mkv
echo "✅ Subtitles hardburned"

# Step 7: Create title overlay file
echo ""
echo "🎨 Step 7/9: Creating title overlay..."
cat > Output/title_overlay.ass << EOF
[Script Info]
ScriptType: v4.00+
PlayResX: 608
PlayResY: 1080

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Title,Noto Sans Bengali,42,&H00FFFFFF,&H000000FF,&H00000000,&H00000000,0,0,0,0,100,100,0,0,3,3,0,8,20,20,1020,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
Dialogue: 0,0:00:00.00,0:00:05.00,Title,,0,0,0,,{\pos(304,60)\an2\bord5\3c&H000000&\4a&H55&}$BENGALI_TITLE
EOF
echo "✅ Title overlay created"

# Step 8: Apply title
echo ""
echo "🎬 Step 8/9: Applying title overlay..."
ffmpeg -y -i Output/reel1_huge_font.mkv \
  -vf "ass=Output/title_overlay.ass" \
  -c:a copy \
  "Output/${OUTPUT_NAME}.mkv"
echo "✅ Title applied"

# Step 9: Summary
echo ""
echo "=================================================="
echo "✨ REEL CREATION COMPLETE! ✨"
echo "=================================================="
echo ""
echo "📍 Final output: Output/${OUTPUT_NAME}.mkv"
echo ""

# Get file info
FILE_SIZE=$(du -h "Output/${OUTPUT_NAME}.mkv" | cut -f1)
DURATION=$(ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 "Output/${OUTPUT_NAME}.mkv" | xargs printf "%.2f")

echo "📊 File size: $FILE_SIZE"
echo "⏱️  Duration: ${DURATION}s"
echo ""
echo "🚀 Ready to upload to:"
echo "   • Instagram Reels"
echo "   • Facebook Reels"
echo "   • YouTube Shorts"
echo ""
echo "=================================================="

# Cleanup temporary files
echo ""
read -p "🗑️  Delete temporary files? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    rm -f Output/reel1.mp4 Output/reel1.txt Output/reel1_enhanced.ass
    rm -f Output/reel1_huge_font.mkv Output/title_overlay.ass
    rm -f podcast_audio.mp3 podcast_audio_transcription.txt
    echo "✅ Cleanup complete"
fi

echo ""
echo "🎉 Done! Happy posting!"
