# TikTok-Style Framing Guide for Bengali Reels

Based on the reference image (6 Truths of Life), here's how to frame your Bengali podcast reels.

---

## 🎯 Framing Requirements

### **Title Specifications**
- **Position:** Top 15% of frame
- **Length:** 3-5 words maximum in Bengali
- **Font:** Large, bold, readable
- **Color:** White text with dark shadow/overlay
- **Background:** Semi-transparent dark overlay for contrast

### **Subtitle Specifications**
- **Position:** Bottom 20-25% of frame
- **Length:** ONE LINE only
- **Font:** Medium size, clean
- **Color:** White with shadow/outline
- **Alignment:** Center-aligned

### **Subject Framing**
- **Position:** Center of frame (60% vertical space)
- **Headroom:** Leave space for title at top
- **Footroom:** Leave space for subtitle at bottom
- **Rule of Thirds:** Center subject for maximum impact

---

## 📝 Bengali Title Examples (3-5 Words)

Based on your current reels, here are optimized titles:

### **Reel 1:** "AI ব্যবহারে আপনার মস্তিষ্ক কি অকেজো হয়ে যাচ্ছে"
**NEW Title (5 words):**
```
আপনার মস্তিষ্ক অকেজো হচ্ছে?
```
**Subtitle (1 line):**
```
AI ব্যবহারে মস্তিষ্কের ক্ষমতা কমে যায়
```

---

### **Reel 2:** "AI যখন নিয়ন্ত্রণের বাইরে যাবে মানবজাতির কী হবে"
**NEW Title (4 words):**
```
AI নিয়ন্ত্রণ হারালে কী হবে?
```
**Subtitle (1 line):**
```
মানবজাতির ভবিষ্যৎ কি বিপদে পড়বে?
```

---

### **Reel 3:** "বিশ্বের সেরা ব্রেইনকে চাকরি দিন মাত্র ২৫০০ টাকায়"
**NEW Title (5 words):**
```
সেরা ব্রেইন মাত্র ২৫০০ টাকায়
```
**Subtitle (1 line):**
```
AI দিয়ে যেকোনো কাজ করান সস্তায়
```

---

## 🎨 ASS Subtitle Template (TikTok Style)

Use this template for creating title overlays:

```ass
[Script Info]
ScriptType: v4.00+
PlayResX: 608
PlayResY: 1080

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding

; Title Style (Top)
Style: Title,Noto Sans Bengali,48,&H00FFFFFF,&H000000FF,&H00000000,&HC0000000,-1,0,0,0,100,100,0,0,1,4,2,8,20,20,920,1

; Subtitle Style (Bottom)
Style: Subtitle,Noto Sans Bengali,36,&H00FFFFFF,&H000000FF,&H00000000,&H80000000,-1,0,0,0,100,100,0,0,1,3,2,2,20,20,100,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text

; Title (appears at top for 5 seconds)
Dialogue: 0,0:00:00.00,0:00:05.00,Title,,0,0,0,,{\pos(304,100)\an2}আপনার মস্তিষ্ক অকেজো হচ্ছে?

; Subtitle (appears throughout video)
Dialogue: 0,0:00:00.00,0:01:14.00,Subtitle,,0,0,0,,{\pos(304,980)\an2}AI ব্যবহারে মস্তিষ্কের ক্ষমতা কমে যায়
```

---

## 📐 Position Guide

```
┌─────────────────────────────┐
│  [15%] TITLE ZONE           │  ← Title: 3-5 Bengali words
│  ──────────────────────     │
│                             │
│                             │
│  [60%] SUBJECT ZONE         │  ← Main video content
│        (centered)           │     Person/scene centered
│                             │
│                             │
│  ──────────────────────     │
│  [25%] SUBTITLE ZONE        │  ← Subtitle: 1 line only
│  + UI ELEMENTS              │     + Like/Share buttons
└─────────────────────────────┘
```

---

## 🔧 Implementation Steps

### **Step 1: Create Title Overlay ASS File**

For each reel, create `title_overlay_tiktok.ass`:

```bash
cd "Projects/AI_Podcast_Rokomari_2025/Processing"

cat > title_overlay_reel1_tiktok.ass << 'EOF'
[Script Info]
ScriptType: v4.00+
PlayResX: 608
PlayResY: 1080

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Title,Noto Sans Bengali,48,&H00FFFFFF,&H000000FF,&H00000000,&HC0000000,-1,0,0,0,100,100,0,0,1,4,2,8,20,20,920,1
Style: Subtitle,Noto Sans Bengali,36,&H00FFFFFF,&H000000FF,&H00000000,&H80000000,-1,0,0,0,100,100,0,0,1,3,2,2,20,20,100,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
Dialogue: 0,0:00:00.00,0:00:05.00,Title,,0,0,0,,{\pos(304,100)\an2}আপনার মস্তিষ্ক অকেজো হচ্ছে?
Dialogue: 0,0:00:00.00,0:01:14.00,Subtitle,,0,0,0,,{\pos(304,980)\an2}AI ব্যবহারে মস্তিষ্কের ক্ষমতা কমে যায়
EOF
```

### **Step 2: Apply to Video**

```bash
# From project directory
cd "Projects/AI_Podcast_Rokomari_2025"

# Apply TikTok-style overlay
ffmpeg -y -i Processing/reel1_huge_font.mkv \
  -vf "ass=Processing/title_overlay_reel1_tiktok.ass" \
  -c:a copy \
  "Output/আপনার_মস্তিষ্ক_অকেজো_হচ্ছে.mkv"
```

---

## 🎨 Design Parameters Explained

### **Title (Top)**
- **Font Size:** 48pt (large, bold, attention-grabbing)
- **Position:** Y=100 (top area, safe zone)
- **Bold:** -1 (enabled for maximum readability)
- **Outline:** 4px black outline
- **Background:** Semi-transparent dark box (&HC0000000)
- **Duration:** 5 seconds (hook)

### **Subtitle (Bottom)**
- **Font Size:** 36pt (readable but smaller than title)
- **Position:** Y=980 (bottom area, above UI)
- **Bold:** -1 (enabled)
- **Outline:** 3px black outline
- **Background:** Lighter semi-transparent (&H80000000)
- **Duration:** Full video length

---

## 📋 Title Writing Rules

### ✅ DO:
- Keep to 3-5 words in Bengali
- Use question format for engagement ("কী হবে?", "হচ্ছে?")
- Front-load the hook word
- Use emojis sparingly (optional)
- Make it scroll-stopping

### ❌ DON'T:
- Don't exceed 5 words
- Don't use multiple lines for title
- Don't use small font
- Don't cover subject's face
- Don't use complex sentences

---

## 🎯 Optimized Titles for All 3 Reels

### **Reel 1: Brain Becoming Useless**
```
Title:    আপনার মস্তিষ্ক অকেজো হচ্ছে?
Subtitle: AI ব্যবহারে মস্তিষ্কের ক্ষমতা কমে যায়
```

### **Reel 2: AI Out of Control**
```
Title:    AI নিয়ন্ত্রণ হারালে কী হবে?
Subtitle: মানবজাতির ভবিষ্যৎ বিপদে পড়বে
```

### **Reel 3: Hire Best Brain**
```
Title:    সেরা ব্রেইন মাত্র ২৫০০ টাকায়
Subtitle: AI দিয়ে যেকোনো কাজ করান
```

---

## 📊 Before vs After Comparison

### **Before (Long Title):**
```
❌ AI ব্যবহারে আপনার মস্তিষ্ক কি অকেজো হয়ে যাচ্ছে
   (13 words - too long, hard to read quickly)
```

### **After (TikTok Style):**
```
✅ আপনার মস্তিষ্ক অকেজো হচ্ছে?
   (4 words - short, punchy, scroll-stopping)
```

---

## 🚀 Quick Command Reference

### **Create All 3 TikTok-Style Reels:**

```bash
cd "Projects/AI_Podcast_Rokomari_2025"

# Reel 1
ffmpeg -y -i Processing/reel1_huge_font.mkv \
  -vf "ass=Processing/title_overlay_reel1_tiktok.ass" \
  -c:a copy "Output/আপনার_মস্তিষ্ক_অকেজো_হচ্ছে.mkv"

# Reel 2
ffmpeg -y -i Processing/reel2_huge_font.mkv \
  -vf "ass=Processing/title_overlay_reel2_tiktok.ass" \
  -c:a copy "Output/AI_নিয়ন্ত্রণ_হারালে_কী_হবে.mkv"

# Reel 3
ffmpeg -y -i Processing/reel3_huge_font.mkv \
  -vf "ass=Processing/title_overlay_reel3_tiktok.ass" \
  -c:a copy "Output/সেরা_ব্রেইন_মাত্র_২৫০০_টাকায়.mkv"
```

---

## ✅ Final Checklist

Before uploading to TikTok/Reels:

- [ ] Title is 3-5 Bengali words
- [ ] Subtitle is ONE line only
- [ ] Title appears for 5 seconds at top
- [ ] Subtitle runs throughout video
- [ ] No text overlaps subject's face
- [ ] Font is bold and readable on mobile
- [ ] Dark background/outline for contrast
- [ ] Video is 608x1080 vertical format
- [ ] Title is attention-grabbing/question format
- [ ] Subtitle provides context/value

---

**Last Updated:** October 19, 2025
**Format:** TikTok/Instagram Reels/YouTube Shorts
**Language:** Bengali (বাংলা)
