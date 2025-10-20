# Migration Guide - v2.0 → v3.0

## Overview

This guide helps you transition from the script-based v2.0 system to the new agentic architecture in v3.0.

---

## 🔑 Key Differences

| Feature | v2.0 (Old) | v3.0 (New) |
|---------|------------|------------|
| Execution | Manual, step-by-step scripts | Automated orchestrator |
| Configuration | Hardcoded in scripts | Central config.yaml |
| Error Handling | Basic | Retry logic + checkpoints |
| Logging | Print statements | Structured logs |
| Monitoring | None | Full metrics |
| Resumability | Manual | Automatic checkpoints |

---

## Installation

### Step 1: Install New Dependencies

```bash
pip install -r requirements-new.txt
```

This installs:
- `pyyaml` for configuration management
- Latest `google-generativeai` package

### Step 2: Verify FFmpeg

The system now auto-validates FFmpeg:

```bash
ffmpeg -version
# Should show: --enable-libass
```

### Step 3: Set Environment Variables

```bash
export GEMINI_API_KEY="your-api-key-here"
```

---

## Usage Comparison

### Old Way (v2.0):

```bash
# Step 1: Extract audio
cd Projects/MyProject
ffmpeg -i Source/video.mp4 -vn -acodec libmp3lame -q:a 2 -t 1800 Transcripts/audio.mp3

# Step 2: Transcribe
cd ../..
python Scripts/transcribe_audio_v2.py Projects/MyProject/Transcripts/audio.mp3

# Step 3: Analyze
python Scripts/analyze_transcript.py Projects/MyProject/Transcripts/audio_transcription.txt

# Step 4-8: Manual steps...
# ... lots of manual execution and checking
```

**Problems:**
- 8+ manual steps
- No error recovery
- No progress tracking
- Hard to debug
- Can't resume if it fails

### New Way (v3.0):

```python
from src.agents.orchestrator import create_orchestrator
from pathlib import Path

# One command - everything automated
orchestrator = create_orchestrator(
    project_name="MyProject",
    source_video=Path("path/to/video.mp4")
)

success = orchestrator.execute_pipeline()
```

**Benefits:**
- Single command
- Automatic error recovery
- Full progress tracking
- Comprehensive logging
- Auto-resume from checkpoints

---

## Configuration Migration

### Old Way: Hardcoded Parameters

```python
# Had to edit each script manually
FONT_SIZE = 68
TITLE_POSITION_Y = 120
MAX_RETRIES = 3
# ... scattered across multiple files
```

### New Way: Central Configuration

Edit `config.yaml`:

```yaml
subtitle:
  title_font_size: 68
  title_position_y: 120

error_handling:
  max_retries: 3

# All settings in one place!
```

---

## Example Migration Scenarios

### Scenario 1: Processing a New Video

**Old Method:**
```bash
# Create project structure manually
mkdir -p Projects/NewPodcast/{Source,Transcripts,Analysis,Processing,Output}

# Copy video
cp ~/Downloads/podcast.mp4 Projects/NewPodcast/Source/

# Run 8 different commands manually
# (see old documentation)
```

**New Method:**
```python
from src.agents.orchestrator import create_orchestrator
from pathlib import Path

# Automatic project creation and processing
orchestrator = create_orchestrator(
    project_name="NewPodcast",
    source_video=Path("~/Downloads/podcast.mp4")
)

orchestrator.execute_pipeline()
# Done! Check Projects/NewPodcast/Output/
```

### Scenario 2: Customizing Subtitle Style

**Old Method:**
```python
# Edit Scripts/text_to_tiktok_ass.py:
# Line 155: Change fontsize=68 to fontsize=75
# Line 156: Change title_position_y=120 to title_position_y=100
# Save, then run script
```

**New Method:**
```yaml
# Edit config.yaml:
subtitle:
  title_font_size: 75
  title_position_y: 100

# Settings apply to all future runs
```

### Scenario 3: Handling API Failures

**Old Method:**
```bash
# API call failed!
# Manually retry:
python Scripts/transcribe_audio_v2.py audio.mp3
# If fails again, give up or edit code
```

**New Method:**
```yaml
# Edit config.yaml:
error_handling:
  max_retries: 5
  retry_delay_seconds: 3.0
  exponential_backoff: true

# Automatic retry with exponential backoff!
# Saves checkpoints - can resume if system crashes
```

---

## Backward Compatibility

### Good News: Old Scripts Still Work!

All your existing scripts remain functional:

```bash
# These still work exactly as before:
python Scripts/transcribe_audio_v2.py audio.mp3
python Scripts/analyze_transcript.py transcript.txt
python Scripts/text_to_tiktok_ass.py words.txt --title "টাইটেল"

# Your existing Projects/ structure is compatible
# No need to migrate old projects
```

### When to Use Old vs New:

**Use Old Scripts When:**
- Quick one-off task
- Testing a single stage
- Working with existing projects
- You prefer manual control

**Use New Orchestrator When:**
- Processing new videos start-to-finish
- Want automatic error handling
- Need progress tracking
- Production use
- Batch processing

---

## Gradual Migration Strategy

### Week 1: Learn the New System
- Read TRANSFORMATION_COMPLETE.md
- Run one test project with orchestrator
- Review generated logs/metrics

### Week 2: Test in Parallel
- Use orchestrator for new projects
- Keep using scripts for critical work
- Compare results

### Week 3: Full Adoption
- Primary tool: orchestrator
- Fallback: scripts (if needed)
- Customize config.yaml to your needs

### Week 4: Advanced Usage
- Set up batch processing
- Tune performance settings
- Integrate with your workflow

---

## Troubleshooting

### "Module not found: src.agents"

**Cause**: Not running from project root

**Solution**:
```bash
cd "/Users/Adnan/Desktop/Long Form to Shorts"
python -c "from src.agents.orchestrator import create_orchestrator; print('OK')"
```

### "Configuration file not found"

**Cause**: config.yaml missing

**Solution**:
```bash
# config.yaml should be in project root
ls config.yaml
# If missing, it was created during transformation
```

### "FFmpeg validation failed"

**Cause**: FFmpeg not installed or no libass

**Solution**:
```bash
# macOS:
brew install ffmpeg

# Linux:
sudo apt install ffmpeg

# Verify:
ffmpeg -version | grep libass
```

### "GEMINI_API_KEY not set"

**Cause**: Environment variable not exported

**Solution**:
```bash
export GEMINI_API_KEY="your-key-here"

# Make permanent (add to ~/.bashrc or ~/.zshrc):
echo 'export GEMINI_API_KEY="your-key"' >> ~/.zshrc
```

---

## Feature Comparison

### Features You Get with v3.0:

#### 1. Automatic Retry Logic
```python
# Old: API fails → manual retry
# New: API fails → auto retry 3 times with backoff
```

#### 2. Progress Tracking
```
Old: No idea where you are
New:
  Stage 1/8: Audio Extraction... ✓ (2.3s)
  Stage 2/8: Transcription... ✓ (45.7s)
  Stage 3/8: Analysis... ✓ (12.1s)
  ...
```

#### 3. Performance Metrics
```json
{
  "execution": {
    "total_duration_seconds": 127.45,
    "stages_completed": 8,
    "stages_failed": 0
  },
  "api": {
    "total_calls": 5,
    "total_tokens_used": 125430,
    "total_cost_usd": 0.0847
  }
}
```

#### 4. Error Recovery
```
Old: Crash at step 5 → start over from step 1
New: Crash at step 5 → resume from step 5 checkpoint
```

#### 5. Structured Logging
```
Old: Random print statements
New:
  2025-10-20 14:23:15 [INFO] Starting pipeline...
  2025-10-20 14:23:17 [INFO] ✓ Audio extraction complete
  2025-10-20 14:24:02 [INFO] ✓ Transcription complete
  # Saved to logs/pipeline.log
```

---

## Configuration Reference

### Essential config.yaml Sections:

```yaml
system:
  log_level: "INFO"      # DEBUG for detailed logs
  max_workers: 4         # Parallel processing threads

api:
  gemini:
    model: "gemini-2.5-pro"
    max_retries: 3
    timeout_seconds: 300

video:
  default_format: "tiktok"    # or "instagram"
  quality:
    crf: 23                    # Lower = better quality (18-28)
    preset: "medium"           # faster = quicker, slower = better

subtitle:
  title_font_size: 68
  subtitle_font_size: 68
  max_words_per_line: 4
  title_duration_seconds: 5.0

error_handling:
  max_retries: 3
  exponential_backoff: true
  save_checkpoints: true       # Enable resume functionality
```

---

## Migration Checklist

- [ ] Install new dependencies: `pip install -r requirements-new.txt`
- [ ] Verify FFmpeg has libass: `ffmpeg -version | grep libass`
- [ ] Set GEMINI_API_KEY environment variable
- [ ] Review config.yaml and adjust settings
- [ ] Test orchestrator with a sample video
- [ ] Review generated logs in Projects/*/Logs/
- [ ] Compare output with old script method
- [ ] Decide on migration timeline
- [ ] Update your documentation/workflows

---

## Getting Help

### Logs Location:
```
Projects/YourProject/Logs/
  ├── pipeline.log      # All execution logs
  ├── errors.log        # Only errors
  ├── pipeline_state.json  # Checkpoint data
  └── metrics.json      # Performance metrics
```

### Check Pipeline Status:
```python
status = orchestrator.get_status()
print(status)
# Shows current stage, errors, duration, etc.
```

### Enable Debug Logging:
```yaml
# config.yaml
system:
  log_level: "DEBUG"  # Very verbose
```

---

## Summary

**The v3.0 system is:**
- ✅ More powerful (automatic orchestration)
- ✅ More reliable (error handling + retry)
- ✅ More observable (logs + metrics)
- ✅ More maintainable (central configuration)
- ✅ Backward compatible (old scripts still work)

**Migration is:**
- ✅ Optional (old scripts still functional)
- ✅ Gradual (use both systems in parallel)
- ✅ Low-risk (no data migration needed)
- ✅ High-reward (better results, less work)

**Recommended approach:**
1. Use orchestrator for all new projects
2. Keep old scripts as fallback
3. Customize config.yaml to your needs
4. Enjoy the automation!

---

**Welcome to v3.0!** 🚀
