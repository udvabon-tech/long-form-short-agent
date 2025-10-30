# Long Form to Shorts Toolkit

Create production-ready Bengali short-form content from long podcasts with two complementary workflows:

1. **Video → Transcript** – Split, transcribe, and clean long-form audio with Gemini.
2. **Transcript → Reel** – Generate vertical reels with styled Bengali subtitles.

Both flows live in this repository so you can reliably respond when someone asks, “Can you transcribe the audio?” *and* “Can you turn this moment into a reel?”

---

## Repository Contents

- `create_reel.py` – Python script that cuts clips and applies Bengali subtitles.
- `video_to_transcript.md` – Full Gemini-based transcription workflow, including prompts and QA steps.
- `AI_fascination_complete_transcription copy.txt` – Example transcript produced with the workflow.
- `README.md` – This quick-start guide.
- `Processing/`, `Output/` – Auto-generated scratch folders (ignored in Git).

---

## Environment Setup

| Requirement | Why you need it | Check |
|-------------|-----------------|-------|
| Python 3.8+ | Runs helper scripts | `python3 --version` |
| FFmpeg (with libass) | Audio extraction + video rendering | `ffmpeg -version \| grep libass` |
| Gemini API key (optional but required for transcription) | Access to Google Generative AI models | `export GEMINI_API_KEY="..."` |
| Bengali fonts (e.g., Noto Sans Bengali) | Clean subtitle rendering | macOS already ships; Linux: `sudo apt install fonts-noto-bengali` |

Install FFmpeg via `brew install ffmpeg` (macOS) or `sudo apt install ffmpeg` (Linux). Windows users can download binaries from [ffmpeg.org](https://ffmpeg.org/download.html).

---

## Quick Start

### 1. Transcribe a Long Video
1. Create a project folder (e.g., `Projects/MyPodcast`).
2. Follow **Video to Transcript - Complete Workflow** (`video_to_transcript.md`) to:
   - Extract audio and split into manageable chunks.
   - Invoke `Scripts/transcribe_audio_v2.py` with the provided prompts.
   - Merge the partial transcripts into a single, chronologically correct file.
3. Validate timestamps and clean up temporary assets.

The guide includes copy/paste prompts, timestamp fix scripts, and QA tips. Keep the resulting `complete_transcription.txt`—you’ll use it for reel generation.
> **Note:** The workflow assumes access to the agent utilities under `Scripts/` (from the full Long Form to Shorts system). If you only need the process outline, substitute the transcription step with your own Gemini API client that accepts custom prompts.

### 2. Create a Reel from a Timestamp Range
```bash
python3 create_reel.py \
  "../AI ফ্যাসিনেশন the 3 destination.mp4" \
  "AI_fascination_complete_transcription copy.txt" \
  "14:21.843" \
  "16:18.063" \
  "অটোনোমাস AI  Agent"
```

What the script does:
- Crops the vertical video segment (`Processing/reel_*_segment.mp4`).
- Generates Bengali subtitle events (`Processing/reel_*.ass`).
- Overlays the title (auto-wrapped, multi-line) and subtitles.
- Delivers the final reel at `Output/reel_<start>_to_<end>.mkv`.

---

## Detailed Usage

### Transcript Format Expectations
```
[14:21.843] Speaker 1: কোডেক্স হচ্ছে আপনি একটা কোড বেজ ওকে কানেক্ট করে দিবেন।
[14:25.123] Speaker 2: অনলাইনে যে কোড বেজ রাখে, ওইটাকে বলে হচ্ছে গিটহাব।
[14:28.456] Speaker 1: গিটহাবে সফটওয়্যারের মেইন কোডগুলা থাকে।
```
- Timestamps must be chronological (`[MM:SS.mmm]` or `[HH:MM:SS.mmm]`).
- Speaker labels can be any consistent format.
- Text should be UTF-8 encoded Bengali (or English when needed).

### create_reel.py Arguments

| Argument | Description |
|----------|-------------|
| `video` | Source video file path. |
| `transcript` | Transcript file with timestamps. |
| `start`, `end` | Clip boundaries (same format as transcript timestamps). |
| `title` | Overlay title (auto-wrapped, multi-line). |
| `--output` | Optional basename for generated files. |

### Title Overlay Tips
- Keep to 2–3 short lines; the script wraps at ~14 characters per line.
- Avoid excessive punctuation to reduce wrap artifacts.
- If you need different wrapping, adjust `wrap_title_text` in `create_reel.py`.

---

## Workflow in Practice

1. **When asked to transcribe audio**  
   - Run through the steps in `video_to_transcript.md`.  
   - Store outputs in `Projects/<Name>/complete_transcription.txt`.  
   - Share QA snippet timestamps to prove accuracy.

2. **When asked to generate a reel**  
   - Point `create_reel.py` at the original video and the transcript you just prepared.  
   - Re-run the script for every interesting clip a stakeholder requests.  
   - Deliver `.mkv` output or convert to `.mp4` with `ffmpeg -i output.mkv output.mp4`.

3. **Hand-off checklist**  
   - Provide the final transcript + the reel(s).  
   - Include the `Processing/` artifacts only if troubleshooting is needed (ignored by default).  
   - Keep prompt files if you customized them—they help reproduce the transcript.

---

## Troubleshooting Cheatsheet

- **FFmpeg not found** – Install and verify `ffmpeg -version`.  
- **libass missing** – Ensure FFmpeg build includes subtitle support.  
- **Subtitle text misaligned** – Confirm transcript timestamps are monotonic.  
- **Title off-screen** – Edit `wrap_title_text` granularity or adjust `\pos` in the ASS template.  
- **Gemini API errors** – Split audio into smaller chunks, re-run failed part, then merge.

---

## Recommended Project Structure

```
Projects/
└── MyPodcast/
    ├── Source/
    │   └── original_video.mp4
    ├── Transcripts/
    │   ├── part1_transcription.txt
    │   ├── part2_transcription.txt
    │   └── complete_transcription.txt
    ├── Processing/
    └── Output/
```

Keep heavy media artifacts out of Git; only commit scripts, prompts, and final transcripts.

---

**Need assistance?**  
Start with `video_to_transcript.md` for transcription nuance, then run `create_reel.py` with the resulting timestamps. Once both workflows are familiar, you can confidently answer either request: “Give me the transcript” or “Give me the reel.”  

**Happy Transcribing and Reel Making! 🎬** 
