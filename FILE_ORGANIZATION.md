# File Organization Guide - Project-Based Structure

This project uses a **project-based organization** where each podcast/content gets its own dedicated folder.

---

## 📁 Main Directory Structure

```
Long Form to Shorts/
│
├── Projects/                      # All content projects
│   ├── AI_Podcast_Rokomari_2025/  # Example project
│   ├── Project_Name_2/
│   └── Project_Name_3/
│
├── Scripts/                       # Shared automation scripts
│   ├── transcribe_audio_v2.py
│   ├── text_to_enhanced_ass.py
│   ├── analyze_transcript.py
│   └── [other scripts]
│
├── Templates/                     # Shared templates
│   └── title_overlay_template.ass
│
├── Input/                         # Staging area (optional)
│   └── [new videos before organizing]
│
├── README.md                      # Main documentation
├── QUICKSTART.md                  # Quick start guide
├── AGENT.md                       # Detailed instructions
└── FILE_ORGANIZATION.md           # This file
```

---

## 📂 Individual Project Structure

Each project in `Projects/` folder follows this structure:

```
Projects/[Project_Name]/
│
├── Source/                        # Original source video
│   └── original_video.mp4
│
├── Transcripts/                   # Audio and transcription
│   ├── audio.mp3
│   └── transcription.txt
│
├── Analysis/                      # AI analysis results
│   ├── REEL_CUT_DIRECTIONS.md
│   └── REELS_SUMMARY.md
│
├── Processing/                    # Intermediate files
│   ├── reel1.mp4
│   ├── reel1.txt
│   ├── reel1_enhanced.ass
│   ├── reel1_huge_font.mkv
│   ├── title_overlay_reel1.ass
│   └── [... same for other reels]
│
└── Output/                        # FINAL REELS ✅
    ├── [Reel_Title_1].mkv
    ├── [Reel_Title_2].mkv
    └── [Reel_Title_3].mkv
```

---

## 🆕 Starting a New Project

### Method 1: Manual Setup

```bash
cd "/Users/Adnan/Desktop/Long Form to Shorts"

# 1. Create project folder (use descriptive name)
PROJECT_NAME="Podcast_Topic_Date"
mkdir -p "Projects/$PROJECT_NAME"/{Source,Transcripts,Analysis,Processing,Output}

# 2. Add your video to the project
cp ~/path/to/video.mp4 "Projects/$PROJECT_NAME/Source/"

# 3. Follow the workflow from the project directory
cd "Projects/$PROJECT_NAME"
```

### Method 2: Using Input Staging Area

```bash
# 1. Drop video in Input/ folder
cp ~/path/to/video.mp4 Input/

# 2. Create project and move video
PROJECT_NAME="My_New_Project"
mkdir -p "Projects/$PROJECT_NAME"/{Source,Transcripts,Analysis,Processing,Output}
mv Input/video.mp4 "Projects/$PROJECT_NAME/Source/"

# 3. Start processing
cd "Projects/$PROJECT_NAME"
```

---

## 📋 Project Naming Convention

**Format:** `[Topic]_[Description]_[Date]`

**Good Examples:**
```
✅ AI_Podcast_Rokomari_2025
✅ Business_Tips_Jan2025
✅ Tech_Review_iPhone16
✅ Interview_JohnDoe_Oct2025
```

**Avoid:**
```
❌ Project 1 (spaces)
❌ new-video (not descriptive)
❌ test (not meaningful)
```

---

## 🔄 Complete Workflow (Project-Based)

### Step 1: Create Project
```bash
PROJECT="My_Podcast_Topic"
cd "/Users/Adnan/Desktop/Long Form to Shorts"
mkdir -p "Projects/$PROJECT"/{Source,Transcripts,Analysis,Processing,Output}
```

### Step 2: Add Source Video
```bash
cp ~/Downloads/podcast.mp4 "Projects/$PROJECT/Source/"
cd "Projects/$PROJECT"
```

### Step 3: Extract Audio
```bash
ffmpeg -i Source/podcast.mp4 -vn -acodec libmp3lame -q:a 2 -t 1800 Transcripts/audio_30min.mp3
```

### Step 4: Transcribe
```bash
cd ../..  # Back to main directory
export GEMINI_API_KEY="your-key"
python3 Scripts/transcribe_audio_v2.py "Projects/$PROJECT/Transcripts/audio_30min.mp3"
```

This creates: `Projects/$PROJECT/Transcripts/audio_30min_transcription.txt`

### Step 5: Analyze for Viral Moments
```bash
python3 Scripts/analyze_transcript.py
# Edit script to point to your project's transcript
```

Results saved to: `Projects/$PROJECT/Analysis/REEL_CUT_DIRECTIONS.md`

### Step 6-8: Create Reels
```bash
cd "Projects/$PROJECT"

# Extract segments, create timestamps, generate subtitles
# All files go into Processing/ folder
# Final reels go into Output/ folder
```

---

## 🗂️ Example: Current Project Structure

```
Projects/AI_Podcast_Rokomari_2025/
│
├── Source/                                 (373 MB)
│   └── আপনি কি জানেন ২০২৫ সালে AI...mp4
│
├── Transcripts/                            (24 MB)
│   ├── podcast_audio_30min.mp3
│   └── podcast_audio_30min_transcription.txt
│
├── Analysis/                               (8.7 KB)
│   ├── REEL_CUT_DIRECTIONS.md
│   └── REELS_SUMMARY.md
│
├── Processing/                             (37 MB)
│   ├── reel1.mp4, reel1.txt, reel1_enhanced.ass
│   ├── reel1_huge_font.mkv, title_overlay_reel1.ass
│   └── [... same for reel2, reel3]
│
└── Output/                                 (18.6 MB) ✅
    ├── AI_ব্যবহারে_আপনার_মস্তিষ্ক_কি_অকেজো_হয়ে_যাচ্ছে.mkv
    ├── AI_যখন_নিয়ন্ত্রণের_বাইরে_যাবে_মানবজাতির_কী_হবে.mkv
    └── বিশ্বের_সেরা_ব্রেইনকে_চাকরি_দিন_মাত্র_২৫০০_টাকায়.mkv
```

---

## 🧹 Cleanup Per Project

### After Reels Are Created:

**Keep:**
```
✅ Source/          # Original video (backup)
✅ Transcripts/     # For re-processing
✅ Analysis/        # For reference
✅ Output/          # Final reels
```

**Can Delete:**
```
❌ Processing/      # Intermediate files (~37 MB)
```

**Cleanup Command:**
```bash
cd "Projects/[Project_Name]"
rm -rf Processing/*
```

### Archive Completed Project:

```bash
# Option 1: Keep in Projects folder (organized)
# No action needed - already organized!

# Option 2: Move to Archive
mkdir -p Archive
mv "Projects/Completed_Project_Name" Archive/

# Option 3: Compress for storage
cd Projects
tar -czf "../Archive/Project_Name_$(date +%Y%m%d).tar.gz" "Project_Name"
rm -rf "Project_Name"
```

---

## 📊 Managing Multiple Projects

### List All Projects:
```bash
cd "/Users/Adnan/Desktop/Long Form to Shorts"
ls -lh Projects/
```

### Find Completed Projects (with Output):
```bash
for project in Projects/*/; do
  if [ -n "$(ls -A "${project}Output/" 2>/dev/null)" ]; then
    echo "✅ Completed: $(basename "$project")"
  fi
done
```

### Total Storage Per Project:
```bash
cd Projects
du -sh */
```

---

## 🔍 Finding Files Across Projects

### Find all final reels:
```bash
find Projects -name "*.mkv" -path "*/Output/*"
```

### Find all transcripts:
```bash
find Projects -name "*transcription.txt"
```

### Find all analysis files:
```bash
find Projects -name "REEL_CUT_DIRECTIONS.md"
```

---

## 📝 Project Metadata (Optional)

Create a `PROJECT_INFO.md` in each project folder:

```bash
cd "Projects/My_Project"
cat > PROJECT_INFO.md << 'EOF'
# Project Information

**Project Name:** AI Podcast - Rokomari 2025
**Source:** Rokomari YouTube Channel
**Date Processed:** October 19, 2025
**Duration:** 1:20:48 (processed first 30 minutes)
**Reels Created:** 3

## Reels

1. **AI ব্যবহারে আপনার মস্তিষ্ক কি অকেজো হয়ে যাচ্ছে?** (1:14)
2. **AI যখন নিয়ন্ত্রণের বাইরে যাবে মানবজাতির কী হবে?** (0:45)
3. **বিশ্বের সেরা ব্রেইনকে চাকরি দিন মাত্র ২৫০০ টাকায়!** (0:32)

## Notes
- High viral potential
- Uploaded to Instagram on [date]
- Facebook engagement: [stats]
EOF
```

---

## 🎯 Benefits of Project-Based Structure

### ✅ Advantages:

1. **Organization:** Each content project is self-contained
2. **Easy to Archive:** Move entire project folder when done
3. **No Conflicts:** Multiple projects don't interfere
4. **Clear History:** Can revisit any project easily
5. **Scalable:** Handle 10s or 100s of projects
6. **Backup Friendly:** Archive or backup specific projects

### ✅ Best For:

- Regular content creators
- Multiple podcast series
- Client work (each client = project)
- Long-term content library

---

## 🔧 Migration from Old Structure

If you have old files in `Input/`, `Output/`, `Transcripts/`:

```bash
cd "/Users/Adnan/Desktop/Long Form to Shorts"

# Create a project for old content
mkdir -p "Projects/Previous_Content"/{Source,Transcripts,Analysis,Processing,Output}

# Move files
mv Input/*.mp4 "Projects/Previous_Content/Source/" 2>/dev/null
mv Transcripts/* "Projects/Previous_Content/Transcripts/" 2>/dev/null
mv Analysis/* "Projects/Previous_Content/Analysis/" 2>/dev/null
mv Output/*.mkv "Projects/Previous_Content/Output/" 2>/dev/null
```

---

## 📚 Quick Reference

### Create New Project:
```bash
PROJECT="New_Project_Name"
mkdir -p "Projects/$PROJECT"/{Source,Transcripts,Analysis,Processing,Output}
```

### Navigate to Project:
```bash
cd "Projects/Project_Name"
```

### List Projects:
```bash
ls Projects/
```

### Clean Project:
```bash
rm -rf "Projects/Project_Name/Processing/*"
```

### Archive Project:
```bash
mv "Projects/Old_Project" Archive/
```

---

**Last Updated:** October 19, 2025
**Structure Version:** 2.0 (Project-Based)
